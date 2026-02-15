from django.contrib import admin
from .models import Course, CourseMaterial, Enrollment, CourseFeedback


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'is_active', 'enrolled_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    date_hierarchy = 'created_at'


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'course__title']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_active', 'is_blocked']
    list_filter = ['is_active', 'is_blocked', 'enrolled_at']
    search_fields = ['student__username', 'course__title']


@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['enrollment__student__username', 'enrollment__course__title']
