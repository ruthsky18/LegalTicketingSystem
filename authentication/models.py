from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Department User'),
        ('admin', 'Legal Admin'),
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
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    
    def is_legal_admin(self):
        return self.role == 'admin'
    
    def is_department_user(self):
        return self.role == 'user'