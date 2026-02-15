from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Course, CourseMaterial, Enrollment, CourseFeedback
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer,
    CourseMaterialSerializer, EnrollmentSerializer, CourseFeedbackSerializer
)
from apps.accounts.permissions import IsTeacher


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Allow teachers to edit, others can only read."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_teacher


class IsCourseOwner(permissions.BasePermission):
    """Only allow course owner to modify."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    
    - List: All users can view active courses
    - Create: Teachers only
    - Update/Delete: Course owner only
    """
    
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        # Teachers can see their own inactive courses
        if self.request.user.is_teacher:
            queryset = Course.objects.filter(teacher=self.request.user) | queryset
        return queryset.distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll the current user in this course."""
        course = self.get_object()
        
        if request.user.is_teacher:
            return Response(
                {'error': 'Teachers cannot enroll in courses.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'is_active': True}
        )
        
        if enrollment.is_blocked:
            return Response(
                {'error': 'You have been blocked from this course.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not created and enrollment.is_active:
            return Response(
                {'message': 'Already enrolled.'},
                status=status.HTTP_200_OK
            )
        
        enrollment.is_active = True
        enrollment.save()
        
        return Response(
            {'message': 'Successfully enrolled.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unenroll(self, request, pk=None):
        """Unenroll the current user from this course."""
        course = self.get_object()
        
        enrollment = get_object_or_404(
            Enrollment, student=request.user, course=course
        )
        enrollment.is_active = False
        enrollment.save()
        
        return Response({'message': 'Successfully unenrolled.'})
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """List enrollments for this course (teacher only)."""
        course = self.get_object()
        
        if course.teacher != request.user:
            return Response(
                {'error': 'Only the course teacher can view enrollments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollments = course.enrollments.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        """List materials for this course."""
        course = self.get_object()
        
        # Check if user has access (enrolled or teacher)
        if not request.user.is_teacher:
            enrollment = Enrollment.objects.filter(
                student=request.user, course=course, is_active=True
            ).first()
            if not enrollment:
                return Response(
                    {'error': 'You must be enrolled to view materials.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        materials = course.materials.all()
        serializer = CourseMaterialSerializer(materials, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing enrollments."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            # Teachers see enrollments in their courses
            return Enrollment.objects.filter(course__teacher=user)
        else:
            # Students see their own enrollments
            return Enrollment.objects.filter(student=user)
