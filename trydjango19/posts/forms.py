'''
Created on 25-Feb-2020

@author: BHADRINATH
'''

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
                "title",
                "content"
            ]