from django.db import models
from django.contrib.auth.models import User



class Quiz(models.Model):
	name = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add=True)
	description = models.TextField()
	num_questions = models.PositiveIntegerField(default=0)
	minutes = models.PositiveIntegerField()
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	
	class Meta:
		ordering = ["name", "-created_at"]
		indexes = [models.Index(fields=['name'])]
	
	def __str__(self):
		return f"Quiz(id={self.id}, name={self.name})"
	

class Question(models.Model):
	text = models.TextField()
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.text
	
	
class Option(models.Model):
	text = models.TextField()
	is_correct = models.BooleanField(default=False)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.text


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	quizes_participated = models.ManyToManyField(Quiz, blank=True)

class Scores(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
	
	
