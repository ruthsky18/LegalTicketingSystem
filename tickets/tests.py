from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date, timedelta
from .models import Ticket, TicketMessage

User = get_user_model()


class TicketManagementFunctionalTests(TestCase):
    """Functional tests for ticket management system"""
    
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
        
        # Create test tickets
        self.ticket1 = Ticket.objects.create(
            user=self.department_user,
            name='John',
            last_name='Doe',
            email='john@example.com',
            department='hr',
            company='company_a',
            contact_number='1234567890',
            nature_of_engagement='for_review',
            details_of_contracting_party='Test contracting party details',
            remarks='Test remarks',
            status='pending',
            priority='medium'
        )
        
        self.ticket2 = Ticket.objects.create(
            user=self.department_user,
            name='Jane',
            last_name='Smith',
            email='jane@example.com',
            department='finance',
            company='company_b',
            contact_number='0987654321',
            nature_of_engagement='for_copy',
            details_of_contracting_party='Another contracting party',
            remarks='Another test remark',
            status='in_progress',
            priority='high'
        )
    
    def test_user_dashboard_access(self):
        """Test department user dashboard access and functionality"""
        # Test unauthenticated access
        response = self.client.get(reverse('tickets:user_dashboard'))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('tickets:user_dashboard')}")
        
        # Test authenticated access
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:user_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify tickets are displayed
        self.assertContains(response, '#1')  # First ticket ID
        self.assertContains(response, '#2')  # Second ticket ID
        self.assertContains(response, 'Pending')
        self.assertContains(response, 'In Progress')
        self.assertContains(response, 'For Review')
        self.assertContains(response, 'For Copy')
    
    def test_create_ticket_functionality(self):
        """Test ticket creation functionality"""
        self.client.login(username='deptuser', password='testpass123')
        
        # Test GET request to create ticket page
        response = self.client.get(reverse('tickets:create_ticket'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request to create ticket
        ticket_data = {
            'name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'department': 'it',
            'company': 'company_c',
            'contact_number': '5555555555',
            'due_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'nature_of_engagement': 'for_access',
            'details_of_contracting_party': 'Test contracting party',
            'remarks': 'Test ticket creation'
        }
        
        response = self.client.post(reverse('tickets:create_ticket'), ticket_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Verify ticket was created
        self.assertTrue(Ticket.objects.filter(name='Test', last_name='User').exists())
        new_ticket = Ticket.objects.get(name='Test', last_name='User')
        self.assertEqual(new_ticket.user, self.department_user)
        self.assertEqual(new_ticket.status, 'pending')
        self.assertEqual(new_ticket.priority, 'medium')
    
    def test_create_ticket_with_document(self):
        """Test ticket creation with document attachment"""
        self.client.login(username='deptuser', password='testpass123')
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        ticket_data = {
            'name': 'Document',
            'last_name': 'Test',
            'email': 'doc@example.com',
            'department': 'legal',
            'company': 'company_d',
            'contact_number': '1111111111',
            'nature_of_engagement': 'for_review',
            'details_of_contracting_party': 'Document test party',
            'remarks': 'Testing document upload',
            'document_attached': test_file
        }
        
        response = self.client.post(reverse('tickets:create_ticket'), ticket_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify ticket with document was created
        ticket = Ticket.objects.get(name='Document', last_name='Test')
        self.assertTrue(ticket.document_attached)
        self.assertTrue(ticket.document_attached.name.startswith('documents/test_document'))
        self.assertTrue(ticket.document_attached.name.endswith('.pdf'))
    
    def test_ticket_detail_view(self):
        """Test ticket detail view for department users"""
        self.client.login(username='deptuser', password='testpass123')
        
        # Test viewing own ticket
        response = self.client.get(reverse('tickets:ticket_detail', args=[self.ticket1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'For Review')  # Display name, not raw value
        
        # Test viewing another user's ticket (should be forbidden)
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            role='user'
        )
        other_ticket = Ticket.objects.create(
            user=other_user,
            name='Other',
            last_name='User',
            email='other@example.com',
            department='hr',
            nature_of_engagement='for_copy'
        )
        
        response = self.client.get(reverse('tickets:ticket_detail', args=[other_ticket.id]))
        self.assertEqual(response.status_code, 404)  # Should not be accessible
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access and functionality"""
        # Test unauthenticated access
        response = self.client.get(reverse('tickets:admin_dashboard'))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('tickets:admin_dashboard')}")
        
        # Test department user access (should redirect to user dashboard)
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('tickets:user_dashboard'))
        
        # Test admin access
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('tickets:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify all tickets are displayed
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')
    
    def test_admin_ticket_filtering(self):
        """Test admin dashboard filtering functionality"""
        self.client.login(username='admin', password='testpass123')
        
        # Test status filtering
        response = self.client.get(reverse('tickets:admin_dashboard'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')  # pending ticket
        self.assertNotContains(response, 'Jane Smith')  # in_progress ticket
        
        # Test department filtering
        response = self.client.get(reverse('tickets:admin_dashboard'), {'department': 'hr'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')  # hr department
        self.assertNotContains(response, 'Jane Smith')  # finance department
        
        # Test company filtering
        response = self.client.get(reverse('tickets:admin_dashboard'), {'company': 'company_a'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')  # company_a
        self.assertNotContains(response, 'Jane Smith')  # company_b
        
        # Test nature filtering
        response = self.client.get(reverse('tickets:admin_dashboard'), {'nature_of_engagement': 'for_review'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')  # for_review
        self.assertNotContains(response, 'Jane Smith')  # for_copy
        
        # Test search functionality
        response = self.client.get(reverse('tickets:admin_dashboard'), {'search': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Jane Smith')
    
    def test_admin_ticket_detail_view(self):
        """Test admin ticket detail view and update functionality"""
        self.client.login(username='admin', password='testpass123')
        
        # Test viewing ticket details
        response = self.client.get(reverse('tickets:admin_ticket_detail', args=[self.ticket1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # Test updating ticket status
        update_data = {
            'status': 'in_progress',
            'admin_comments': 'Ticket is now being processed',
            'priority': 'high',
            'assigned_to': self.admin_user.id
        }
        
        response = self.client.post(reverse('tickets:admin_ticket_detail', args=[self.ticket1.id]), update_data)
        self.assertEqual(response.status_code, 302)  # Redirect after update
        
        # Verify ticket was updated
        updated_ticket = Ticket.objects.get(id=self.ticket1.id)
        self.assertEqual(updated_ticket.status, 'in_progress')
        self.assertEqual(updated_ticket.admin_comments, 'Ticket is now being processed')
        self.assertEqual(updated_ticket.priority, 'high')
        self.assertEqual(updated_ticket.assigned_to, self.admin_user)
    
    def test_admin_ticket_completion(self):
        """Test admin completing a ticket with reviewed document"""
        self.client.login(username='admin', password='testpass123')
        
        # Create a test reviewed document
        reviewed_file = SimpleUploadedFile(
            "reviewed_document.pdf",
            b"reviewed_content",
            content_type="application/pdf"
        )
        
        completion_data = {
            'status': 'completed',
            'admin_comments': 'Ticket completed successfully',
            'priority': 'medium',
            'reviewed_document': reviewed_file
        }
        
        response = self.client.post(reverse('tickets:admin_ticket_detail', args=[self.ticket1.id]), completion_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify ticket completion
        completed_ticket = Ticket.objects.get(id=self.ticket1.id)
        self.assertEqual(completed_ticket.status, 'completed')
        self.assertTrue(completed_ticket.reviewed_document)
        self.assertTrue(completed_ticket.reviewed_document.name.startswith('reviewed_documents/reviewed_document'))
        self.assertTrue(completed_ticket.reviewed_document.name.endswith('.pdf'))
    
    def test_ticket_pagination(self):
        """Test pagination functionality"""
        self.client.login(username='deptuser', password='testpass123')
        
        # Create additional tickets to test pagination
        for i in range(15):
            Ticket.objects.create(
                user=self.department_user,
                name=f'User{i}',
                last_name='Test',
                email=f'user{i}@example.com',
                department='hr',
                nature_of_engagement='for_copy'
            )
        
        # Test first page
        response = self.client.get(reverse('tickets:user_dashboard'))
        self.assertEqual(response.status_code, 200)
        # Should contain some tickets (first 10)
        
        # Test second page
        response = self.client.get(reverse('tickets:user_dashboard'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        # Should contain tickets from second page
    
    def test_ticket_priority_and_status_badges(self):
        """Test ticket priority and status badge functionality"""
        # Test status badge classes
        self.assertEqual(self.ticket1.get_status_badge_class(), 'warning')  # pending
        self.assertEqual(self.ticket2.get_status_badge_class(), 'info')  # in_progress
        
        # Test priority badge classes
        self.assertEqual(self.ticket1.get_priority_badge_class(), 'warning')  # medium
        self.assertEqual(self.ticket2.get_priority_badge_class(), 'danger')  # high
        
        # Test completed status
        self.ticket1.status = 'completed'
        self.assertEqual(self.ticket1.get_status_badge_class(), 'success')
        
        # Test critical priority
        self.ticket1.priority = 'critical'
        self.assertEqual(self.ticket1.get_priority_badge_class(), 'dark')


class TicketConversationFunctionalTests(TestCase):
    """Functional tests for ticket conversation system"""
    
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
        
        # Create test ticket
        self.ticket = Ticket.objects.create(
            user=self.department_user,
            name='John',
            last_name='Doe',
            email='john@example.com',
            department='hr',
            company='company_a',
            contact_number='1234567890',
            nature_of_engagement='for_review',
            details_of_contracting_party='Test contracting party details',
            remarks='Test remarks',
            status='pending',
            priority='medium'
        )
    
    def test_admin_conversation_access(self):
        """Test admin conversation access and functionality"""
        # Test unauthenticated access
        response = self.client.get(reverse('tickets:ticket_conversation', args=[self.ticket.id]))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('tickets:ticket_conversation', args=[self.ticket.id])}")
        
        # Test department user access (should redirect to user dashboard)
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('tickets:user_dashboard'))
        
        # Test admin access
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('tickets:ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
    
    def test_admin_send_message(self):
        """Test admin sending messages in conversation"""
        self.client.login(username='admin', password='testpass123')
        
        # Test sending a message
        message_data = {
            'message': 'This is an admin message to the user'
        }
        
        response = self.client.post(reverse('tickets:ticket_conversation', args=[self.ticket.id]), message_data)
        self.assertEqual(response.status_code, 302)  # Redirect after sending
        
        # Verify message was created
        self.assertTrue(TicketMessage.objects.filter(ticket=self.ticket, sender=self.admin_user).exists())
        message = TicketMessage.objects.get(ticket=self.ticket, sender=self.admin_user)
        self.assertEqual(message.message, 'This is an admin message to the user')
        self.assertTrue(message.is_admin_message)
        self.assertFalse(message.is_read)
    
    def test_admin_send_message_with_attachment(self):
        """Test admin sending messages with attachments"""
        self.client.login(username='admin', password='testpass123')
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "admin_attachment.pdf",
            b"attachment_content",
            content_type="application/pdf"
        )
        
        message_data = {
            'message': 'Admin message with attachment',
            'attachment': test_file
        }
        
        response = self.client.post(reverse('tickets:ticket_conversation', args=[self.ticket.id]), message_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify message with attachment was created
        message = TicketMessage.objects.get(ticket=self.ticket, sender=self.admin_user)
        self.assertTrue(message.attachment)
        self.assertTrue(message.attachment.name.startswith('message_attachments/admin_attachment'))
        self.assertTrue(message.attachment.name.endswith('.pdf'))
    
    def test_user_conversation_access(self):
        """Test user conversation access and functionality"""
        # Test unauthenticated access
        response = self.client.get(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]))
        self.assertRedirects(response, f"{reverse('auth:login')}?next={reverse('tickets:user_ticket_conversation', args=[self.ticket.id])}")
        
        # Test admin access (should redirect to admin dashboard)
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('tickets:admin_dashboard'))
        
        # Test user access to own ticket
        self.client.logout()
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
    
    def test_user_send_message(self):
        """Test user sending messages in conversation"""
        self.client.login(username='deptuser', password='testpass123')
        
        # Test sending a message
        message_data = {
            'message': 'This is a user message to the admin'
        }
        
        response = self.client.post(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]), message_data)
        self.assertEqual(response.status_code, 302)  # Redirect after sending
        
        # Verify message was created
        self.assertTrue(TicketMessage.objects.filter(ticket=self.ticket, sender=self.department_user).exists())
        message = TicketMessage.objects.get(ticket=self.ticket, sender=self.department_user)
        self.assertEqual(message.message, 'This is a user message to the admin')
        self.assertFalse(message.is_admin_message)
        self.assertFalse(message.is_read)
    
    def test_conversation_thread(self):
        """Test full conversation thread between admin and user"""
        # Admin sends first message
        self.client.login(username='admin', password='testpass123')
        admin_message_data = {'message': 'Admin: Hello, I received your ticket.'}
        self.client.post(reverse('tickets:ticket_conversation', args=[self.ticket.id]), admin_message_data)
        
        # User responds
        self.client.logout()
        self.client.login(username='deptuser', password='testpass123')
        user_message_data = {'message': 'User: Thank you for the quick response.'}
        self.client.post(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]), user_message_data)
        
        # Admin responds again
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        admin_message_data2 = {'message': 'Admin: You are welcome. We will process this soon.'}
        self.client.post(reverse('tickets:ticket_conversation', args=[self.ticket.id]), admin_message_data2)
        
        # Verify all messages exist
        messages = TicketMessage.objects.filter(ticket=self.ticket).order_by('created_at')
        self.assertEqual(messages.count(), 3)
        
        # Verify message order and content
        self.assertEqual(messages[0].message, 'Admin: Hello, I received your ticket.')
        self.assertTrue(messages[0].is_admin_message)
        
        self.assertEqual(messages[1].message, 'User: Thank you for the quick response.')
        self.assertFalse(messages[1].is_admin_message)
        
        self.assertEqual(messages[2].message, 'Admin: You are welcome. We will process this soon.')
        self.assertTrue(messages[2].is_admin_message)
    
    def test_message_read_status(self):
        """Test message read status functionality"""
        # Create admin message
        admin_message = TicketMessage.objects.create(
            ticket=self.ticket,
            sender=self.admin_user,
            message='Admin message',
            is_admin_message=True
        )
        
        # Create user message
        user_message = TicketMessage.objects.create(
            ticket=self.ticket,
            sender=self.department_user,
            message='User message',
            is_admin_message=False
        )
        
        # Test admin viewing conversation (should mark user messages as read)
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('tickets:ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify user messages are marked as read
        user_message.refresh_from_db()
        self.assertTrue(user_message.is_read)
        
        # Test user viewing conversation (should mark admin messages as read)
        self.client.logout()
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:user_ticket_conversation', args=[self.ticket.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify admin messages are marked as read
        admin_message.refresh_from_db()
        self.assertTrue(admin_message.is_read)
    
    def test_user_cannot_access_other_user_ticket_conversation(self):
        """Test that users cannot access other users' ticket conversations"""
        # Create another user and ticket
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            role='user'
        )
        other_ticket = Ticket.objects.create(
            user=other_user,
            name='Other',
            last_name='User',
            email='other@example.com',
            department='hr',
            nature_of_engagement='for_copy'
        )
        
        # Test accessing other user's ticket conversation
        self.client.login(username='deptuser', password='testpass123')
        response = self.client.get(reverse('tickets:user_ticket_conversation', args=[other_ticket.id]))
        self.assertEqual(response.status_code, 404)  # Should not be accessible
