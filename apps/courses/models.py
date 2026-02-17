from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

# Get storage for raw files (PDFs/docs)
# In production, uses Cloudinary; in development, uses default file storage
def get_material_storage():
    from django.conf import settings
    if hasattr(settings, 'CLOUDINARY_STORAGE') and settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    return None  # Uses DEFAULT_FILE_STORAGE


def course_material_path(instance, filename):
    """Generate upload path: elearning/courses/{course_slug}/{filename}"""
    course_slug = slugify(instance.course.title)
    return f'elearning/courses/{course_slug}/{filename}'


class Course(models.Model):
    """Course model - created and managed by teachers."""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_teaching'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def enrolled_count(self):
        return self.enrollments.filter(is_active=True).count()
    
    @property
    def average_rating(self):
        from apps.courses.models import CourseFeedback
        feedbacks = CourseFeedback.objects.filter(enrollment__course=self)
        if feedbacks.exists():
            return round(sum(f.rating for f in feedbacks) / feedbacks.count(), 1)
        return None


class CourseMaterial(models.Model):
    """Course materials uploaded by teachers."""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=course_material_path,
        storage=get_material_storage
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Enrollment(models.Model):
    """Student enrollment in a course."""
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class CourseFeedback(models.Model):
    """Feedback/review left by enrolled students."""
    
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.enrollment.course.title} by {self.enrollment.student.username}"
    
    @property
    def course(self):
        return self.enrollment.course
    
    @property
    def student(self):
        return self.enrollment.student
