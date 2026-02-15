from django import forms
from .models import Course, CourseMaterial, CourseFeedback


class CourseForm(forms.ModelForm):
    """Form for creating and editing courses."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Course description',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CourseMaterialForm(forms.ModelForm):
    """Form for uploading course materials."""
    
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Material title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description (optional)',
                'rows': 2
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class CourseFeedbackForm(forms.ModelForm):
    """Form for leaving course feedback."""
    
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rating (1-5 stars)'
    )
    
    class Meta:
        model = CourseFeedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this course (optional)',
                'rows': 3
            }),
        }
