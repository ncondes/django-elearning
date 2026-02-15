from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.courses.models import Course, CourseMaterial, Enrollment, CourseFeedback

User = get_user_model()


class CourseModelTest(TestCase):
    """Tests for the Course model."""
    
    def setUp(self):
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
            description='A test course description',
            teacher=self.teacher
        )
    
    def test_course_creation(self):
        """Test course is created correctly."""
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.teacher, self.teacher)
        self.assertTrue(self.course.is_active)
    
    def test_course_str(self):
        """Test course string representation."""
        self.assertEqual(str(self.course), 'Test Course')
    
    def test_enrolled_count(self):
        """Test enrolled_count property."""
        self.assertEqual(self.course.enrolled_count, 0)
        Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(self.course.enrolled_count, 1)
    
    def test_average_rating_none(self):
        """Test average_rating returns None when no feedback."""
        self.assertIsNone(self.course.average_rating)
    
    def test_average_rating_calculation(self):
        """Test average_rating calculation."""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        CourseFeedback.objects.create(enrollment=enrollment, rating=4)
        self.assertEqual(self.course.average_rating, 4.0)


class EnrollmentModelTest(TestCase):
    """Tests for the Enrollment model."""
    
    def setUp(self):
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
    
    def test_enrollment_creation(self):
        """Test enrollment is created correctly."""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_active)
        self.assertFalse(enrollment.is_blocked)
    
    def test_enrollment_unique_together(self):
        """Test student can only enroll once per course."""
        Enrollment.objects.create(student=self.student, course=self.course)
        with self.assertRaises(Exception):
            Enrollment.objects.create(student=self.student, course=self.course)


class CourseFeedbackModelTest(TestCase):
    """Tests for the CourseFeedback model."""
    
    def setUp(self):
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
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
    
    def test_feedback_creation(self):
        """Test feedback is created correctly."""
        feedback = CourseFeedback.objects.create(
            enrollment=self.enrollment,
            rating=5,
            comment='Great course!'
        )
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, 'Great course!')
    
    def test_feedback_properties(self):
        """Test feedback course and student properties."""
        feedback = CourseFeedback.objects.create(
            enrollment=self.enrollment,
            rating=4
        )
        self.assertEqual(feedback.course, self.course)
        self.assertEqual(feedback.student, self.student)
