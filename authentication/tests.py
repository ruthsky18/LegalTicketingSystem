from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from tickets.models import Ticket, TicketMessage

User = get_user_model()


class AuthenticationFunctionalTests(TestCase):
    """Functional tests for authentication system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.department_user = User.objects.create_user(
            username='deptuser',
            email='dept@example.com',
            password='testpass123',
            first_name='Department',
            last_name='User',
            role='user'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
    
    def test_department_user_signup(self):
        """Test department user signup functionality"""
        response = self.client.get(reverse('auth:signup'))
        self.assertEqual(response.status_code, 200)
        
        # Test signup form submission
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'user'
        }
        
        response = self.client.post(reverse('auth:signup'), signup_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.role, 'user')
        self.assertTrue(new_user.is_department_user())
    
    def test_admin_user_signup(self):
        """Test admin user signup functionality"""
        signup_data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'admin'
        }
        
        response = self.client.post(reverse('auth:signup'), signup_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify admin user was created
        self.assertTrue(User.objects.filter(username='newadmin').exists())
        new_admin = User.objects.get(username='newadmin')
        self.assertEqual(new_admin.role, 'admin')
        self.assertTrue(new_admin.is_legal_admin())
    
    def test_department_user_login(self):
        """Test department user login functionality"""
        # Test department user login
        login_data = {
            'username': 'deptuser',
            'password': 'testpass123',
            'user_type': 'department'
        }
        
        response = self.client.post(reverse('auth:login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tickets:user_dashboard'))
        
        # Verify user is logged in
        response = self.client.get(reverse('tickets:user_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_user_login(self):
        """Test admin user login functionality"""
        login_data = {
            'username': 'admin',
            'password': 'testpass123',
            'user_type': 'legal'
        }
        
        response = self.client.post(reverse('auth:login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tickets:admin_dashboard'))
        
        # Verify admin is logged in
        response = self.client.get(reverse('tickets:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_wrong_role_login_attempt(self):
        """Test login with wrong role selection"""
        # Department user trying to login as legal admin
        login_data = {
            'username': 'deptuser',
            'password': 'testpass123',
            'user_type': 'legal'
        }
        
        response = self.client.post(reverse('auth:login'), login_data)
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        self.assertContains(response, 'not authorized for legal team access')
    
    def test_invalid_credentials_login(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'deptuser',
            'password': 'wrongpassword',
            'user_type': 'department'
        }
        
        response = self.client.post(reverse('auth:login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_logout_functionality(self):
        """Test user logout functionality"""
        # Login first
        self.client.login(username='deptuser', password='testpass123')
        
        # Test logout
        response = self.client.post(reverse('auth:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth:login'))
        
        # Verify user is logged out
        response = self.client.get(reverse('tickets:user_dashboard'))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('tickets:user_dashboard')}")
    
    def test_profile_access(self):
        """Test profile page access"""
        # Test unauthenticated access
        response = self.client.get(reverse('auth:profile'))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('auth:profile')}")
        
        # Test authenticated access
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('auth:profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_redirect_for_authenticated_users(self):
        """Test home page redirects for authenticated users"""
        # Test department user redirect
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:home'))
        self.assertRedirects(response, reverse('tickets:user_dashboard'))
        
        # Test admin user redirect
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('tickets:home'))
        self.assertRedirects(response, reverse('tickets:admin_dashboard'))
    
    def test_home_redirect_for_unauthenticated_users(self):
        """Test home page redirect for unauthenticated users"""
        response = self.client.get(reverse('tickets:home'))
        self.assertRedirects(response, reverse('auth:login'))
