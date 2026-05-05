from django import forms
from home.models import Comment


"""
class CommentForm(forms.Form):
	name = forms.CharField()
	comment = forms.CharField(
		widget=forms.Textarea(attrs={"rows": "6", "cols": "50"})
	)
"""

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ["comment"]
		widgets = {
			"rows": "6",
			"cols": "50"
		}
