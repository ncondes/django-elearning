from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, StudentProfile, TeacherProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create the appropriate profile when a new user is created."""
    if created:
        if instance.user_type == User.UserType.STUDENT:
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == User.UserType.TEACHER:
            TeacherProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile exists and is saved when user is saved."""
    if instance.user_type == User.UserType.STUDENT:
        if not hasattr(instance, 'student_profile'):
            StudentProfile.objects.create(user=instance)
    elif instance.user_type == User.UserType.TEACHER:
        if not hasattr(instance, 'teacher_profile'):
            TeacherProfile.objects.create(user=instance)
