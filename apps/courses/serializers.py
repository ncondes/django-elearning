from rest_framework import serializers
from .models import Course, CourseMaterial, Enrollment, CourseFeedback
from apps.accounts.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested representations."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'user_type']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CourseMaterialSerializer(serializers.ModelSerializer):
    """Serializer for course materials."""
    
    class Meta:
        model = CourseMaterial
        fields = ['id', 'title', 'description', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class CourseFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for course feedback."""
    
    student = UserMinimalSerializer(source='enrollment.student', read_only=True)
    
    class Meta:
        model = CourseFeedback
        fields = ['id', 'student', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments."""
    
    student = UserMinimalSerializer(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'enrolled_at', 'is_active', 'is_blocked']
        read_only_fields = ['enrolled_at']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view."""
    
    teacher = UserMinimalSerializer(read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'enrolled_count', 
                  'average_rating', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view."""
    
    teacher = UserMinimalSerializer(read_only=True)
    materials = CourseMaterialSerializer(many=True, read_only=True)
    feedbacks = serializers.SerializerMethodField()
    enrolled_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'materials', 
                  'feedbacks', 'enrolled_count', 'average_rating', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_feedbacks(self, obj):
        feedbacks = CourseFeedback.objects.filter(enrollment__course=obj)
        return CourseFeedbackSerializer(feedbacks, many=True).data


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses."""
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'is_active']
