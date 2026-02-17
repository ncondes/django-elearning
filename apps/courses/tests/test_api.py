from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.courses.models import Course, Enrollment, CourseMaterial

User = get_user_model()


class CourseAPITest(TestCase):
    """Tests for the Course API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.teacher2 = User.objects.create_user(
            username='teacher2',
            email='teacher2@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            user_type='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
    
    def test_list_courses_unauthenticated(self):
        """Test that unauthenticated users cannot list courses."""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_courses_authenticated(self):
        """Test listing courses for authenticated user."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated with 'results' key
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)
    
    def test_retrieve_course(self):
        """Test retrieving a single course."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')
    
    def test_create_course_teacher(self):
        """Test that teachers can create courses."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/courses/', {
            'title': 'New Course',
            'description': 'A new course'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Course.objects.filter(title='New Course').exists())
    
    def test_create_course_student_forbidden(self):
        """Test that students cannot create courses."""
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/courses/', {
            'title': 'New Course',
            'description': 'A new course'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_course_owner(self):
        """Test that course owner can update course."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(f'/api/courses/{self.course.pk}/', {
            'title': 'Updated Course'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')
    
    def test_update_course_non_owner_forbidden(self):
        """Test that non-owner teacher cannot update course."""
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.patch(f'/api/courses/{self.course.pk}/', {
            'title': 'Hacked Course'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_course_owner(self):
        """Test that course owner can delete course."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(f'/api/courses/{self.course.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())


class EnrollmentAPITest(TestCase):
    """Tests for enrollment API actions."""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            user_type='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
    
    def test_enroll_student(self):
        """Test student can enroll via API."""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.pk}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(
            student=self.student, course=self.course
        ).exists())
    
    def test_enroll_teacher_forbidden(self):
        """Test teacher cannot enroll in courses."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f'/api/courses/{self.course.pk}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_enroll_blocked_student(self):
        """Test blocked student cannot re-enroll."""
        Enrollment.objects.create(
            student=self.student, course=self.course, is_blocked=True
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.pk}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unenroll_student(self):
        """Test student can unenroll via API."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f'/api/courses/{self.course.pk}/unenroll/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        self.assertFalse(enrollment.is_active)
    
    def test_list_enrollments_student(self):
        """Test student sees their own enrollments."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated with 'results' key
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)
    
    def test_list_enrollments_teacher(self):
        """Test teacher sees enrollments in their courses."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated with 'results' key
        self.assertIn('results', response.data)
        self.assertGreaterEqual(response.data['count'], 1)
    
    def test_course_enrollments_action(self):
        """Test teacher can view course enrollments via action."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/courses/{self.course.pk}/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_course_enrollments_non_owner_forbidden(self):
        """Test non-owner cannot view course enrollments."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.pk}/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MaterialsAPITest(TestCase):
    """Tests for course materials API."""
    
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpass123',
            user_type='student'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
    
    def test_materials_enrolled_student(self):
        """Test enrolled student can view materials."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.pk}/materials/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_materials_unenrolled_student_forbidden(self):
        """Test unenrolled student cannot view materials."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(f'/api/courses/{self.course.pk}/materials/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_materials_teacher(self):
        """Test teacher can view materials."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f'/api/courses/{self.course.pk}/materials/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
