from django import forms
from django.contrib.auth.models import User
from projects.models import ProjectCategory
from django.contrib.auth.forms import UserCreationForm

class SignUpForm2(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    email = forms.EmailField(max_length=254, help_text='Inform a valid email address.')
    email_confirmation = forms.EmailField(max_length=254, help_text='Enter the same email as before, for verification.')
    
    city = forms.CharField(max_length=50)
    postal_code = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'email_confirmation', 'city', 'postal_code',)
