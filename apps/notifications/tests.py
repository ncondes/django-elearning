from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.notifications.models import Notification
from apps.courses.models import Course, Enrollment, CourseMaterial, CourseFeedback

User = get_user_model()


class NotificationModelTest(TestCase):
    """Tests for the Notification model."""
    
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
    
    def test_notification_creation(self):
        """Test notification is created correctly."""
        notification = Notification.objects.create(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='New Enrollment',
            message='A student enrolled in your course.',
            course=self.course,
            actor=self.student
        )
        self.assertEqual(notification.recipient, self.teacher)
        self.assertFalse(notification.is_read)
    
    def test_notification_str(self):
        """Test notification string representation."""
        notification = Notification.objects.create(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='New Enrollment',
            message='Test message'
        )
        self.assertIn('enrollment', str(notification))
        self.assertIn('teacher1', str(notification))
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='New Enrollment',
            message='Test message'
        )
        self.assertFalse(notification.is_read)
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
    
    def test_notification_ordering(self):
        """Test notifications are ordered by created_at descending."""
        n1 = Notification.objects.create(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='First',
            message='First notification'
        )
        n2 = Notification.objects.create(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.NEW_MATERIAL,
            title='Second',
            message='Second notification'
        )
        notifications = Notification.objects.filter(recipient=self.teacher)
        self.assertEqual(notifications[0], n2)
        self.assertEqual(notifications[1], n1)


class NotificationSignalsTest(TestCase):
    """Tests for notification signals."""
    
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
    
    def test_enrollment_creates_notification(self):
        """Test that enrolling creates notification for teacher."""
        Enrollment.objects.create(student=self.student, course=self.course)
        notification = Notification.objects.filter(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.ENROLLMENT
        ).first()
        self.assertIsNotNone(notification)
        self.assertIn('student1', notification.message)
    
    def test_new_material_creates_notification(self):
        """Test that uploading material notifies enrolled students."""
        Enrollment.objects.create(student=self.student, course=self.course)
        CourseMaterial.objects.create(
            course=self.course,
            title='Test Material',
            file='test.pdf'
        )
        notification = Notification.objects.filter(
            recipient=self.student,
            notification_type=Notification.NotificationType.NEW_MATERIAL
        ).first()
        self.assertIsNotNone(notification)
    
    def test_feedback_creates_notification(self):
        """Test that leaving feedback notifies teacher."""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        CourseFeedback.objects.create(
            enrollment=enrollment,
            rating=5,
            comment='Great course!'
        )
        notification = Notification.objects.filter(
            recipient=self.teacher,
            notification_type=Notification.NotificationType.NEW_RATING
        ).first()
        self.assertIsNotNone(notification)


class NotificationViewsTest(TestCase):
    """Tests for notification views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.ENROLLMENT,
            title='Test Notification',
            message='Test message'
        )
    
    def test_notification_list_requires_login(self):
        """Test notification list requires authentication."""
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 302)
    
    def test_notification_list_authenticated(self):
        """Test notification list for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('notifications:mark_as_read', kwargs={'pk': self.notification.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read."""
        Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.NEW_MATERIAL,
            title='Another Notification',
            message='Another message'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('notifications:mark_all_as_read'))
        self.assertEqual(response.status_code, 302)
        unread = Notification.objects.filter(recipient=self.user, is_read=False).count()
        self.assertEqual(unread, 0)
    
    def test_unread_count_ajax(self):
        """Test unread count endpoint."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications:unread_count'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
    
    def test_cannot_mark_other_user_notification(self):
        """Test user cannot mark another user's notification as read."""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='other', password='testpass123')
        response = self.client.post(
            reverse('notifications:mark_as_read', kwargs={'pk': self.notification.pk})
        )
        self.assertEqual(response.status_code, 404)
