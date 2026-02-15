from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Enrollment, CourseFeedback

User = get_user_model()


class CourseViewsTest(TestCase):
    """Tests for course views."""
    
    def setUp(self):
        self.client = Client()
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
    
    def test_course_list_requires_login(self):
        """Test course list requires authentication."""
        response = self.client.get(reverse('courses:course_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_course_list_authenticated(self):
        """Test course list for authenticated user."""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
    
    def test_course_detail(self):
        """Test course detail view."""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:course_detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
    
    def test_course_create_teacher_only(self):
        """Test only teachers can create courses."""
        # Student should be forbidden
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:course_create'))
        self.assertEqual(response.status_code, 403)
        
        # Teacher should have access
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:course_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_course_create_post(self):
        """Test teacher can create a course."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.post(reverse('courses:course_create'), {
            'title': 'New Course',
            'description': 'A new course description',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(title='New Course').exists())
    
    def test_enroll_course(self):
        """Test student can enroll in a course."""
        self.client.login(username='student1', password='testpass123')
        response = self.client.post(reverse('courses:enroll', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())
    
    def test_teacher_cannot_enroll(self):
        """Test teacher cannot enroll in courses."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.post(reverse('courses:enroll', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Enrollment.objects.filter(student=self.teacher, course=self.course).exists())
    
    def test_unenroll_course(self):
        """Test student can unenroll from a course."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student1', password='testpass123')
        response = self.client.post(reverse('courses:unenroll', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        self.assertFalse(enrollment.is_active)


class UserSearchViewTest(TestCase):
    """Tests for user search view."""
    
    def setUp(self):
        self.client = Client()
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
            user_type='student',
            first_name='John',
            last_name='Doe'
        )
    
    def test_search_requires_teacher(self):
        """Test only teachers can access user search."""
        # Student should be forbidden
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('courses:user_search'))
        self.assertEqual(response.status_code, 403)
        
        # Teacher should have access
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:user_search'))
        self.assertEqual(response.status_code, 200)
    
    def test_search_by_username(self):
        """Test search by username."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:user_search'), {'q': 'student1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')
    
    def test_search_by_name(self):
        """Test search by name."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('courses:user_search'), {'q': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')
