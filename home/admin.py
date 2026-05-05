from django.contrib import admin
from home.models import Quiz, Question, Option, UserProfile
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class TimeListFilter(admin.SimpleListFilter):
	title = "Available Time"
	parameter_name = "interval"
	
	def lookups(self, request, model_admin):
		
		result = [("60", "<1 hr"), ("120", "1-2 hrs")]
		return result
	
	def queryset(self, request, queryset):
		start = self.value()
		if start is None:
			return queryset
		
		start = int(start)
		result = queryset.filter(
			minutes__gte=start-60,
			minutes__lte=start,
		)
		return result
	


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'minutes', 'num_questions', 'show_weekday', 'show_questions')
	list_filter = (TimeListFilter, )
	search_fields = ('name',)
	
	def show_weekday(self, obj):
		return obj.created_at.strftime("%A")
	show_weekday.short_description = "Creation Weekday"

	def show_questions(self, obj):
		questions = obj.question_set.all()
		if len(questions) == 0:
			return format_html("<i>None</i>")
		
		plural = ""
		if len(questions) > 1:
			plural = "s"
			
		param = "?id__in=" + ",".join([str(q.id) for q in questions])
		url = reverse("admin:home_question_changelist") + param
		return format_html('<a href="{}">Question{}</a>', url, plural)
	show_questions.short_description = "Questions"
	



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'text', 'quiz')



@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
	list_display = ('id', 'text', 'question', 'is_correct')



class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	
class UserAdmin(BaseUserAdmin):
	inlines = [UserProfileInline]
	
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

