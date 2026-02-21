from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, StatusUpdate


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with user type selection."""
    
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=User.UserType.choices,
        widget=forms.RadioSelect,
        initial=User.UserType.STUDENT,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'username': 'Choose a username',
            'email': 'your.email@example.com',
            'first_name': 'Your first name',
            'last_name': 'Your last name',
            'password1': 'Create a password',
            'password2': 'Confirm your password',
        }
        
        for field_name, field in self.fields.items():
            if field_name != 'user_type':
                field.widget.attrs['class'] = 'form-control'
                if field_name in placeholders:
                    field.widget.attrs['placeholder'] = placeholders[field_name]
                field.help_text = ''
                field.widget.attrs['required'] = False


class UserLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['username'].widget.attrs['required'] = False
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password'].widget.attrs['required'] = False


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'photo', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StatusUpdateForm(forms.ModelForm):
    """Form for creating status updates."""
    
    class Meta:
        model = StatusUpdate
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': "What's on your mind?",
                'class': 'form-control',
            }),
        }
