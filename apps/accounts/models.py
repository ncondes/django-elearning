from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom User model with user_type field."""
    
    class UserType(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.STUDENT,
    )
    photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
    )
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})

    @property
    def is_teacher(self):
        return self.user_type == self.UserType.TEACHER

    @property
    def is_student(self):
        return self.user_type == self.UserType.STUDENT


class StudentProfile(models.Model):
    """Extended profile for students."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"Student: {self.user.username}"


class TeacherProfile(models.Model):
    """Extended profile for teachers."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
    )
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Teacher: {self.user.username}"


class StatusUpdate(models.Model):
    """Status updates for user home pages."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='status_updates',
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
