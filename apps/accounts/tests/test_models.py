from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.accounts.models import StudentProfile, TeacherProfile, StatusUpdate

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for the custom User model."""
    
    def test_create_student_user(self):
        """Test creating a student user."""
        user = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            user_type=User.UserType.STUDENT,
        )
        self.assertEqual(user.username, 'teststudent')
        self.assertEqual(user.email, 'student@test.com')
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_teacher)
        self.assertTrue(hasattr(user, 'student_profile'))
    
    def test_create_teacher_user(self):
        """Test creating a teacher user."""
        user = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            user_type=User.UserType.TEACHER,
        )
        self.assertEqual(user.username, 'testteacher')
        self.assertTrue(user.is_teacher)
        self.assertFalse(user.is_student)
        self.assertTrue(hasattr(user, 'teacher_profile'))
    
    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
        self.assertEqual(str(user), 'testuser')
    
    def test_user_absolute_url(self):
        """Test user get_absolute_url method."""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
        self.assertEqual(user.get_absolute_url(), '/accounts/profile/testuser/')


class StudentProfileTest(TestCase):
    """Tests for StudentProfile model."""
    
    def test_student_profile_created_automatically(self):
        """Test that StudentProfile is created when a student user is created."""
        user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            user_type=User.UserType.STUDENT,
        )
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        self.assertFalse(user.student_profile.is_blocked)
    
    def test_student_profile_str(self):
        """Test StudentProfile string representation."""
        user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            user_type=User.UserType.STUDENT,
        )
        self.assertEqual(str(user.student_profile), 'Student: student')


class TeacherProfileTest(TestCase):
    """Tests for TeacherProfile model."""
    
    def test_teacher_profile_created_automatically(self):
        """Test that TeacherProfile is created when a teacher user is created."""
        user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            user_type=User.UserType.TEACHER,
        )
        self.assertTrue(TeacherProfile.objects.filter(user=user).exists())
    
    def test_teacher_profile_str(self):
        """Test TeacherProfile string representation."""
        user = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            user_type=User.UserType.TEACHER,
        )
        self.assertEqual(str(user.teacher_profile), 'Teacher: teacher')


class StatusUpdateTest(TestCase):
    """Tests for StatusUpdate model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
    
    def test_create_status_update(self):
        """Test creating a status update."""
        status = StatusUpdate.objects.create(
            user=self.user,
            content='This is a test status update.',
        )
        self.assertEqual(status.user, self.user)
        self.assertEqual(status.content, 'This is a test status update.')
    
    def test_status_update_str(self):
        """Test StatusUpdate string representation."""
        status = StatusUpdate.objects.create(
            user=self.user,
            content='This is a test status update that is quite long.',
        )
        self.assertIn('testuser:', str(status))
    
    def test_status_update_ordering(self):
        """Test that status updates are ordered by created_at descending."""
        status1 = StatusUpdate.objects.create(user=self.user, content='First')
        status2 = StatusUpdate.objects.create(user=self.user, content='Second')
        
        statuses = StatusUpdate.objects.all()
        self.assertEqual(statuses[0], status2)
        self.assertEqual(statuses[1], status1)
