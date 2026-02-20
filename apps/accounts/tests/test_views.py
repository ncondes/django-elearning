from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.accounts.models import StatusUpdate

User = get_user_model()


class RegisterViewTest(TestCase):
    """Tests for the registration view."""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
    
    def test_register_page_loads(self):
        """Test that the registration page loads correctly."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_student(self):
        """Test registering a new student."""
        response = self.client.post(self.register_url, {
            'username': 'newstudent',
            'email': 'student@test.com',
            'first_name': 'Test',
            'last_name': 'Student',
            'user_type': 'student',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        user = User.objects.get(username='newstudent')
        self.assertTrue(user.is_student)
    
    def test_register_teacher(self):
        """Test registering a new teacher."""
        response = self.client.post(self.register_url, {
            'username': 'newteacher',
            'email': 'teacher@test.com',
            'first_name': 'Test',
            'last_name': 'Teacher',
            'user_type': 'teacher',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newteacher')
        self.assertTrue(user.is_teacher)


class LoginViewTest(TestCase):
    """Tests for the login view."""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
    
    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
    
    def test_login_failure(self):
        """Test login with wrong password."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertContains(response, 'Please enter a correct username and password')


class HomeViewTest(TestCase):
    """Tests for the home view (redirects to courses)."""
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('accounts:home')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
    
    def test_home_requires_login(self):
        """Test that home page requires authentication."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_home_redirects_to_courses(self):
        """Test that home page redirects to courses for authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)  # Redirects to courses
        self.assertIn('courses', response.url)


class PostsViewTest(TestCase):
    """Tests for the posts view."""
    
    def setUp(self):
        self.client = Client()
        self.posts_url = reverse('posts')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
    
    def test_posts_requires_login(self):
        """Test that posts page requires authentication."""
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_posts_page_loads_for_authenticated_user(self):
        """Test that posts page loads for authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/posts.html')
    
    def test_post_status_update(self):
        """Test posting a status update."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.posts_url, {
            'content': 'This is my status update!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after post
        self.assertTrue(StatusUpdate.objects.filter(
            user=self.user,
            content='This is my status update!'
        ).exists())


class ProfileViewTest(TestCase):
    """Tests for the profile view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
        self.profile_url = reverse('accounts:profile', kwargs={'username': 'testuser'})
    
    def test_profile_page_loads(self):
        """Test that profile page loads correctly."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'testuser')
    
    def test_profile_shows_status_updates(self):
        """Test that profile shows user's status updates."""
        StatusUpdate.objects.create(user=self.user, content='Test status')
        response = self.client.get(self.profile_url)
        self.assertContains(response, 'Test status')


class ProfileEditViewTest(TestCase):
    """Tests for the profile edit view."""
    
    def setUp(self):
        self.client = Client()
        self.edit_url = reverse('accounts:profile_edit')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
        )
    
    def test_edit_requires_login(self):
        """Test that profile edit requires authentication."""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
    
    def test_edit_page_loads(self):
        """Test that edit page loads for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit.html')
    
    def test_update_profile(self):
        """Test updating user profile."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.edit_url, {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'bio': 'My new bio',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.bio, 'My new bio')
