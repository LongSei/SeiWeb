from django import forms
from .models import Profile, Blog
from django.contrib.auth.models import User

class LoginForm(forms.ModelForm):
    username = forms.CharField(required=True)    
    password = forms.CharField(required=True)

    class Meta: 
        model = Profile
        fields = ['username']

class SignupForm(forms.ModelForm): 
    name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta: 
        model = Profile
        fields = ['username']

class DeletePostForm(forms.ModelForm): 
    id = forms.IntegerField(required=True)
    class Meta:
        model = Blog
        fields = ['id']

class PostBlog(forms.ModelForm): 
    header = forms.CharField(required=True)
    description = forms.CharField(required=True)

    class Meta: 
        model = Blog
        fields = ['id']

class ChangeProfileForm(forms.ModelForm): 
    class Meta: 
        model = Profile
        fields = '__all__'