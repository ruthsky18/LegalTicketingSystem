from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    NATURE_CHOICES = [
        ('for_copy', 'For Copy'),
        ('for_review', 'For Review'),
        ('for_access', 'For Access'),
        ('for_data_breach', 'For Data Breach Notification'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('hr', 'HR'),
        ('finance', 'Finance'),
        ('it', 'IT'),
        ('marketing', 'Marketing'),
        ('operations', 'Operations'),
        ('legal', 'Legal'),
        ('other', 'Other'),
    ]
    
    COMPANY_CHOICES = [
        ('company_a', 'Medicare Plus Inc.'),
        ('company_b', 'Care Center'),
        ('company_c', 'Vidacure'),
        ('company_d', 'Company D'),
        ('company_e', 'Company E'),
        ('other', 'Other'),
    ]
    
    # User information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    
    # Basic ticket information
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    company = models.CharField(max_length=20, choices=COMPANY_CHOICES, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Dates
    date_created = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    
    # Request details
    nature_of_engagement = models.CharField(max_length=20, choices=NATURE_CHOICES)
    document_attached = models.FileField(upload_to='documents/', blank=True, null=True)
    details_of_contracting_party = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    # Admin fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comments = models.TextField(blank=True, null=True)
    reviewed_document = models.FileField(upload_to='reviewed_documents/', blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_tickets', limit_choices_to={'role': 'admin'})
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Timestamps
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.nature_of_engagement} by {self.name} {self.last_name}"
    
    def get_status_badge_class(self):
        status_classes = {
            'pending': 'warning',
            'in_progress': 'info',
            'completed': 'success',
            'rejected': 'danger',
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_priority_badge_class(self):
        priority_classes = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark',
        }
        return priority_classes.get(self.priority, 'secondary')


class TicketMessage(models.Model):
    """Model for conversation threads between admin and requestor"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_admin_message = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} on Ticket #{self.ticket.id}"