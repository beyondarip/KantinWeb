from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full rounded-lg border-gray-300 focus:border-secondary focus:ring-secondary',
        'placeholder': 'Masukkan email anda'
    }))
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full rounded-lg border-gray-300 focus:border-secondary focus:ring-secondary',
        'placeholder': 'Masukkan username'
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full rounded-lg border-gray-300 focus:border-secondary focus:ring-secondary',
        'placeholder': 'Masukkan password'
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full rounded-lg border-gray-300 focus:border-secondary focus:ring-secondary',
        'placeholder': 'Konfirmasi password'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom label
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Konfirmasi Password'

        # Remove default help texts
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'address')