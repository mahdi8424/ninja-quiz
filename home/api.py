from ninja import Router, ModelSchema, Field, FilterSchema, Query
from home.models import Quiz, Question, Option
from django.shortcuts import get_object_or_404
from django.urls import reverse
from typing import Optional
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ninja.errors import HttpError


router = Router()



@router.get('/')
def home(request):
	return "Main path"



#################################### Option ####################################

class OptionOut(ModelSchema):
	class Meta:
		model = Option
		fields = ['id', 'text', 'is_correct', 'question']

class OptionIn(ModelSchema):
	class Meta:
		model = Option
		fields = ['text', 'is_correct', 'question']

class OptionPut(ModelSchema):
	class Meta:
		model = Option
		fields = ['text', 'is_correct']
		
		
@router.get("/option/{option_id}/", response=OptionOut)
def option(request, option_id):
	option = get_object_or_404(Option, id=option_id)
	return option

@router.post("/option/", response=OptionOut, auth=JWTAuth())
def create_option(request, payload: OptionIn):
	data = payload.dict()
	data["question"] = get_object_or_404(Question, id=data["question"])
	option = Option.objects.create(**data)
	return option

@router.put("/option/{option_id}/", response=OptionOut, auth=JWTAuth())
def update_option(request, option_id, payload: OptionPut):
	option = get_object_or_404(Option, id=option_id)
	for key, value in payload.dict().items():
		setattr(option, key, value)
	option.save()
	return option

@router.delete("/option/{option_id}/", auth=JWTAuth())
def delete_option(request, option_id):
	option = get_object_or_404(Option, id=option_id)
	option.delete()
	return {"success": True}


#################################### Question ####################################

class QuestionOut(ModelSchema):
	options: list[OptionOut] = Field(..., alias='option_set')
	class Meta:
		model = Question
		fields = ['id', 'text', 'quiz']

class QuestionIn(ModelSchema):
	class Meta:
		model = Question
		fields = ['text', 'quiz']

class QuestionPut(ModelSchema):
	class Meta:
		model = Question
		fields = ['text']


@router.get("/question/{question_id}/", response=QuestionOut)
def question(request, question_id):
	question = get_object_or_404(Question, id=question_id)
	return question

@router.post("/question/", response=QuestionOut, auth=JWTAuth())
def create_question(request, payload: QuestionIn):
	data = payload.dict()
	data["quiz"] = get_object_or_404(Quiz, id=data["quiz"])
	question = Question.objects.create(**data)
	return question

@router.put("/question/{question_id}/", response=QuestionOut, auth=JWTAuth())
def update_question(request, question_id, payload: QuestionPut):
	question = get_object_or_404(Question, id=question_id)
	data = payload.dict()
	for key, value in data.items():
		setattr(question, key, value)
	question.save()
	return question

@router.delete("/question/{question_id}/", auth=JWTAuth())
def delete_question(request, question_id):
	question = get_object_or_404(Question, id=question_id)
	question.delete()
	return {"success": True}


@receiver(post_save, sender=Question)
def question_post_save(sender, **kwargs):
	if kwargs['created'] and not kwargs['raw']:
		question = kwargs['instance']
		question.quiz.num_questions += 1
		question.quiz.save()
		
@receiver(post_delete, sender=Question)
def question_post_delete(sender, instance, **kwargs):
	instance.quiz.num_questions -= 1
	instance.quiz.save()
	
####################################   Quiz   ####################################

class QuizOut(ModelSchema):
	
	url: str
	author: str
	class Meta:
		model = Quiz
		fields = ["id", "name", "description", "created_at", "num_questions", "minutes"]
		
	@staticmethod
	def resolve_url(obj):
		url = reverse("api-1.0:fetch_quiz", args=[obj.id, ])
		return url
	
	@staticmethod
	def resolve_author(obj):
		username = obj.author.username
		return username


class QuizFullOut(ModelSchema):

	questions: list[QuestionOut] = Field(..., alias="question_set")
	author: str
	class Meta:
		model = Quiz
		fields = ["id", "name", "description", "created_at", "num_questions", "minutes", "author"]
	
	@staticmethod
	def resolve_author(obj):
		username = obj.author.username
		return username

class QuizIn(ModelSchema):
	class Meta:
		model = Quiz
		fields = ["name", "description", "minutes"]


class QuizFilter(FilterSchema):
	name: Optional[str] = Field(None, q=['name__istartswith'])


@router.get("/quizes/", response=list[QuizOut])
def quizes(request, filters: QuizFilter = Query(...)):
	quizes = Quiz.objects.all()
	quizes = filters.filter(quizes)
	return quizes

@router.get("/quiz/{quiz_id}/", response=QuizFullOut, url_name="fetch_quiz")
def quiz(request, quiz_id):
	quiz = get_object_or_404(Quiz, id=quiz_id)
	return quiz


@router.post("/quiz/", response=QuizOut, auth=JWTAuth())
def create_quiz(request, payload:QuizIn):
	data = payload.dict()
	data["author"] = request.user
	quiz = Quiz.objects.create(**data)
	return quiz

@router.put("/quiz/{quiz_id}/", response=QuizOut, auth=JWTAuth())
def update_quiz(request, quiz_id, payload:QuizIn):
	quiz = get_object_or_404(Quiz, id=quiz_id)
	for key, value in payload.dict().items():
		setattr(quiz, key, value)
	quiz.save()
	return quiz

@router.delete("/quiz/{quiz_id}/", auth=JWTAuth())
def delete_quiz(request, quiz_id):
	quiz = get_object_or_404(Quiz, id=quiz_id)
	if request.user.id == quiz.author.id:
		quiz.delete()
		return {"success": True}
	return {"success": False}



#################################### User ####################################

class UserOut(ModelSchema):
	class Meta:
		model = User
		fields = ['id', 'username', 'first_name', 'last_name']

class UserFullOut(ModelSchema):
	quizes: list[QuizOut] = Field(..., alias="quiz_set")
	class Meta:
		model = User
		fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
					'is_active', 'groups', 'user_permissions', 'last_login']


class UserIn(ModelSchema):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name', 'email']


class UserPut(ModelSchema):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'is_active']

@router.get("/me/", response=UserFullOut, auth=JWTAuth())
def get_me(request):
	user = get_object_or_404(User, id=request.user.id)
	return user
	
@router.get("/users/", response=list[UserOut])
def all_users(request):
	users = User.objects.all()
	return users

@router.get("/user/{user_id}/", response=UserOut)
def get_user(request, user_id):
	
	user = get_object_or_404(User, id=user_id)
	return user

@router.post("/user/")
def create_user(request, payload:UserIn):
	if User.objects.filter(username=payload.username).exists():
		return {"success":False, "error": "Username already exists"}
	if User.objects.filter(email=payload.email).exists():
		return {"success": False, "error": "Email already in use"}
	user = User.objects.create_user(**payload.dict())
	return {"success": True, "user_id": user.id, "username": user.username,
			"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
		
@router.put("/update_user/", response=UserFullOut, auth=JWTAuth())
def update_user(request, payload: UserPut):
	user = get_object_or_404(User, id=request.user.id)
	for key, value in payload.dict().items():
		setattr(user, key, value)
	user.save()
	return user
	
@router.delete("/delete_user/", auth=JWTAuth())
def delete_user(request):
	user = get_object_or_404(User, id=request.user.id)
	user.delete()
	return {"success": True}


#################################### Staff ####################################

class UserInStaff(ModelSchema):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']

class UserPutStaff(ModelSchema):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'is_active', 'is_staff']
		
		
@router.get("/staff/user/{user_id}/", response=UserFullOut, auth=JWTAuth())
def staff_get_user(request, user_id):
	if request.user.is_staff:
		user = get_object_or_404(User, id=user_id)
		return user
	raise HttpError(403, "Staff Only")

@router.post("/staff/create_user/", auth=JWTAuth())
def staff_create_user(request, payload: UserInStaff):
	if request.user.is_staff:
		if User.objects.filter(username=payload.username).exists():
			return {"success": False, "error": "Username already exists"}, 400
		if User.objects.filter(email=payload.email).exists():
			return {"success": False, "error": "Email already in use"}, 400
		user = User.objects.create_user(**payload.dict())
		return {"success": True, "user_id": user.id, "username": user.username,
				"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
	raise HttpError(403, "Staff Only")
	
@router.put("/staff/update_user/{user_id}/", response=UserFullOut, auth=JWTAuth())
def staff_update_user(request, user_id, payload: UserPutStaff):
	if request.user.is_staff:
		user = get_object_or_404(User, id=user_id)
		for key, value in payload.dict().items():
			setattr(user, key, value)
		user.save()
		return user
	raise HttpError(403, "Staff Only")
	
@router.delete("/staff/delete_user/{user_id}/", auth=JWTAuth())
def staff_delete_user(request, user_id):
	if request.user.is_staff:
		user = get_object_or_404(User, id=user_id)
		user.delete()
		return {"success": True}
	raise HttpError(403, "Staff Only")
