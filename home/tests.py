from django.test import TestCase
from home.models import Quiz, Question, Option
from datetime import date
from django.contrib.auth.models import User
from ninja.testing import TestClient
from home.api import router
from ninja_jwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404



class TestHome(TestCase):
	
	def setUp(self):
		
		self.PASSWORD = '1234'
		self.owner = User.objects.create_user(username='owner', password=self.PASSWORD, is_staff=True)
		self.member = User.objects.create_user(username='member', password=self.PASSWORD)
		self.quiz = Quiz.objects.create(name="Russian Lang", description="All essential russian vocabularies", minutes=120, author=self.owner)
		self.question = Question.objects.create(text="nyet", quiz=self.quiz)
		self.option_1 = Option.objects.create(text="No", is_correct=True, question=self.question)
		self.option_2 = Option.objects.create(text="Yes", question=self.question)
		self.client = TestClient(router)
		refresh = RefreshToken.for_user(self.owner)
		refresh_member = RefreshToken.for_user(self.member)
		access_token = str(refresh.access_token)
		access_member = str(refresh_member.access_token)
				
		self.headers = {
			"Authorization": f"Bearer {access_token}"
		}
		
		self.headers_member = {
			"Authorization": f"Bearer {access_member}"
		}

	def test_quiz_get(self):
		
		url = f"/quiz/{self.quiz.id}/"
		response = self.client.get(url)

		self.assertEqual(200, response.status_code)
		res = response.json()
		self.assertEqual(res['id'], self.quiz.id)
		self.assertEqual(res['name'], self.quiz.name)
		self.assertEqual(res['num_questions'], 1)
		self.assertEqual(res['description'], self.quiz.description)
		self.assertEqual(res['minutes'], self.quiz.minutes)
		self.assertEqual(res['author'], self.quiz.author.username)
		self.assertEqual(res['questions'][0]['text'], "nyet")
		self.assertEqual(res['questions'][0]['options'][0]['text'], "No")
		self.assertEqual(res['questions'][0]['options'][1]['is_correct'], False)
	
	def test_quiz_get_404(self):
		

		url = f'/quiz/999/'
		response = self.client.get(url)
		self.assertEqual(404, response.status_code)
		
		
	def test_quiz_create(self):
		
		url = f"/quiz/"
		
		data = {
			"name": "test quiz",
			"description": "testing our api",
			"minutes": 20,
		}
		
		response = self.client.post(url, json=data, headers=self.headers)
		self.assertEqual(200, response.status_code)
		res = response.json()
		self.assertEqual(res['id'], 2)
		self.assertEqual(res['name'], data["name"])
		self.assertEqual(res['description'], data["description"])
		self.assertEqual(res['num_questions'], 0)
		self.assertEqual(res['minutes'], data["minutes"])
		self.assertEqual(res['author'], "owner")
	
	
	def test_quiz_put(self):
		
		url = f"/quiz/1/"
		data = {
			"name": self.quiz.name,
			"description": self.quiz.description,
			"minutes": 25
		}
		quiz = get_object_or_404(Quiz, id=1)
		for key, value in data.items():
			setattr(Quiz, key, value)
		
		response = self.client.put(url, json=data, headers=self.headers)
		self.assertEqual(200, response.status_code)
		res = response.json()
		self.assertEqual(res['id'], 1)
		self.assertEqual(res['name'], data["name"])
		self.assertEqual(res['description'], data["description"])
		self.assertEqual(res['num_questions'], 1)
		self.assertEqual(res['minutes'], data["minutes"])
		self.assertEqual(res['author'], "owner")
		
	def test_quiz_delete(self):
		
		url = f"/quiz/{self.quiz.id}/"
		
		response = self.client.delete(url, headers=self.headers)
		self.assertEqual(response.json()["success"], True)
	
	def test_question_create(self):
		
		url = f"/question/"
		data = {"text": "privet", "quiz_id": Quiz.objects.first().id,}
		
		response = self.client.post(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		
		url = f"/question/{res['id']}/"
		
		response = self.client.get(url, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['text'], data['text'])
		self.assertEqual(res['quiz'], data['quiz_id'])
	
	def test_question_put(self):
		
		url = f"/question/{self.question.id}/"
		data = {"text": "Privet"}
		
		response = self.client.put(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['id'], self.question.id)
		self.assertEqual(res['text'], data['text'])
		self.assertEqual(res['quiz'], self.quiz.id)
	
	
	def test_question_delete(self):
		
		url = f"/question/{self.question.id}/"
		
		response = self.client.delete(url, headers=self.headers)
		self.assertEqual(response.json()["success"], True)	
		
	def test_option_create(self):
		
		url = f"/option/"
		data = {"text": "that's ok", "is_correct": False, "question_id": self.question.id}
		
		response = self.client.post(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		
		url = f"/option/{res['id']}/"
		
		response = self.client.get(url, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['text'], data['text'])
		self.assertEqual(res['is_correct'], data['is_correct'])
		self.assertEqual(res['question'], data['question_id'])
		
	def test_option_put(self):
		
		url = f"/option/{self.option_1.id}/"
		data = {"text": self.option_1.text, "is_correct":False}
		
		response = self.client.put(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['id'], self.option_1.id)
		self.assertEqual(res['text'], self.option_1.text)
		self.assertEqual(res['is_correct'], data["is_correct"])
	
	def test_option_delete(self):
		
		url = f"/option/{self.option_1.id}/"
		
		response = self.client.delete(url, headers=self.headers)
		self.assertEqual(response.json()["success"], True)
		
	
	def test_user_me(self):
		
		url = "/me/"
		
		response = self.client.get(url, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['username'], self.owner.username)
	
	def test_user_get(self):
		
		url = f"/user/{self.member.id}/"
		
		response = self.client.get(url, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['username'], self.member.username)
	
	def test_user_create(self):
		
		url = "/user/"
		data = {
			"first_name": "Mahdi",
			"last_name": "Ba",
			"username": "Mahdi8424",
			"email": "mahdi@member.com",
			"password": "member1234",
		}
		
		response = self.client.post(url, json=data)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res["username"], data["username"])
		self.assertEqual(res["email"], data["email"])
		
		response = self.client.post(url, json=data)
		res = response.json()
		self.assertEqual(res["success"], False)
	
	def test_user_put(self):
		
		url = f"/update_user/"
		data = {"first_name": "Mahdi", "last_name": "Ba", "username": self.member.username,
				"email": "mahdi@member.com", "is_active": True}
		
		response = self.client.put(url, json=data, headers=self.headers_member)
		res = response.json()
		self.assertEqual(200, response.status_code)
		for key, value in data.items():
			self.assertEqual(res[key], value)
			
	def test_user_delete(self):
		
		url = "/delete_user/"
		
		response = self.client.delete(url, headers=self.headers_member)
		self.assertEqual(200, response.status_code)
		self.assertEqual(response.json()["success"], True)
	
	def test_user_get_staff(self):
		
		url = f"/staff/user/{self.member.id}/"
		
		response = self.client.get(url, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res['username'], self.member.username)
		
		response = self.client.get(url, headers=self.headers_member)
		self.assertEqual(403, response.status_code)
	
	def test_user_create_staff(self):
		
		url = "/staff/create_user/"
		data = {
			"first_name": "Mahdi",
			"last_name": "Ba",
			"username": "Mahdi8424",
			"email": "mahdi@member.com",
			"password": "member1234",
		}
		
		response = self.client.post(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		self.assertEqual(res["username"], data["username"])
		self.assertEqual(res["email"], data["email"])
		
		response = self.client.post(url, json=data, headers=self.headers_member)
		res = response.json()
		self.assertEqual(403, response.status_code)
	
	def test_user_put_staff(self):
		
		url = f"/staff/update_user/{self.member.id}/"
		data = {"first_name": "Mahdi", "last_name": "Ba", "username": self.member.username,
				"email": "mahdi@member.com", "is_active": True}
		
		response = self.client.put(url, json=data, headers=self.headers)
		res = response.json()
		self.assertEqual(200, response.status_code)
		for key, value in data.items():
			self.assertEqual(res[key], value)
		
		response = self.client.put(url, json=data, headers=self.headers_member)
		res = response.json()
		self.assertEqual(403, response.status_code)
			
	def test_user_delete_staff(self):
		
		url = f"/staff/delete_user/{self.member.id}/"
		
		response = self.client.delete(url, headers=self.headers_member)
		self.assertEqual(403, response.status_code)
		
		response = self.client.delete(url, headers=self.headers)
		self.assertEqual(200, response.status_code)
		self.assertEqual(response.json()["success"], True)
		
		
	
	

