from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.chat.models import ChatRoom, ChatMessage, OnlineUser
from apps.courses.models import Course, Enrollment

User = get_user_model()


class ChatRoomModelTest(TestCase):
    """Tests for the ChatRoom model."""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
    
    def test_chatroom_creation(self):
        """Test chat room is created correctly."""
        room = ChatRoom.objects.create(course=self.course)
        self.assertEqual(room.course, self.course)
    
    def test_chatroom_str(self):
        """Test chat room string representation."""
        room = ChatRoom.objects.create(course=self.course)
        self.assertIn('Test Course', str(room))
    
    def test_get_online_users(self):
        """Test getting online users."""
        room = ChatRoom.objects.create(course=self.course)
        self.assertEqual(room.get_online_users().count(), 0)
        OnlineUser.objects.create(room=room, user=self.teacher)
        self.assertEqual(room.get_online_users().count(), 1)


class ChatMessageModelTest(TestCase):
    """Tests for the ChatMessage model."""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
        self.room = ChatRoom.objects.create(course=self.course)
    
    def test_message_creation(self):
        """Test message is created correctly."""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.teacher,
            content='Hello, world!'
        )
        self.assertEqual(message.content, 'Hello, world!')
        self.assertEqual(message.user, self.teacher)
    
    def test_message_str(self):
        """Test message string representation."""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.teacher,
            content='Hello, world!'
        )
        self.assertIn('teacher1', str(message))
        self.assertIn('Hello', str(message))
    
    def test_message_ordering(self):
        """Test messages are ordered by created_at ascending."""
        m1 = ChatMessage.objects.create(room=self.room, user=self.teacher, content='First')
        m2 = ChatMessage.objects.create(room=self.room, user=self.teacher, content='Second')
        messages = ChatMessage.objects.filter(room=self.room)
        self.assertEqual(messages[0], m1)
        self.assertEqual(messages[1], m2)


class OnlineUserModelTest(TestCase):
    """Tests for the OnlineUser model."""
    
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@example.com',
            password='testpass123',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course',
            teacher=self.teacher
        )
        self.room = ChatRoom.objects.create(course=self.course)
    
    def test_online_user_creation(self):
        """Test online user is created correctly."""
        online = OnlineUser.objects.create(room=self.room, user=self.teacher)
        self.assertEqual(online.user, self.teacher)
        self.assertEqual(online.room, self.room)
    
    def test_online_user_unique_together(self):
        """Test user can only be online once per room."""
        OnlineUser.objects.create(room=self.room, user=self.teacher)
        with self.assertRaises(Exception):
            OnlineUser.objects.create(room=self.room, user=self.teacher)


class ChatViewsTest(TestCase):
    """Tests for chat views."""
    
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
        self.room = ChatRoom.objects.create(course=self.course)
    
    def test_chat_room_requires_login(self):
        """Test chat room requires authentication."""
        response = self.client.get(reverse('chat:room', kwargs={'course_pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_chat_room_teacher_access(self):
        """Test teacher can access their course chat room."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('chat:room', kwargs={'course_pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_chat_room_enrolled_student_access(self):
        """Test enrolled student can access chat room."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:room', kwargs={'course_pk': self.course.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_chat_room_unenrolled_student_denied(self):
        """Test unenrolled student cannot access chat room."""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:room', kwargs={'course_pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_chat_room_blocked_student_denied(self):
        """Test blocked student cannot access chat room."""
        Enrollment.objects.create(student=self.student, course=self.course, is_blocked=True)
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:room', kwargs={'course_pk': self.course.pk}))
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_get_user_chats_teacher(self):
        """Test teacher gets their course chats."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('chat:user_chats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['chats']), 1)
        self.assertEqual(data['chats'][0]['course_title'], 'Test Course')
    
    def test_get_user_chats_student(self):
        """Test student gets their enrolled course chats."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:user_chats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['chats']), 1)
    
    def test_get_chat_messages_teacher(self):
        """Test teacher can get chat messages."""
        ChatMessage.objects.create(room=self.room, user=self.teacher, content='Test message')
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('chat:get_messages', kwargs={'room_id': self.room.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['messages']), 1)
    
    def test_get_chat_messages_unenrolled_denied(self):
        """Test unenrolled student cannot get chat messages."""
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:get_messages', kwargs={'room_id': self.room.id}))
        self.assertEqual(response.status_code, 403)
    
    def test_get_chat_messages_enrolled_student(self):
        """Test enrolled student can get chat messages."""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat:get_messages', kwargs={'room_id': self.room.id}))
        self.assertEqual(response.status_code, 200)
