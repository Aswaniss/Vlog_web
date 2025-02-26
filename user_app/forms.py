from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message']  # Only 'message' field is needed
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Write your comment...', 'rows': 5, 'class': 'form-control'})
        }
        labels = {'message': ''}  # No label needed for the message
        
 

from .models import Vlog



from django import forms



