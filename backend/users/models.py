from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import uuid

# Custom user model extending Djangos AbstractUser
class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None # Remove username field
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    # Fields for use
    USERNAME_FIELD = 'email' # Use email for authentication, not username
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager() # Custom manager for user model
    
    
    class Meta:
        """Class for defining user table constraints and indexes"""
        db_table = 'users'
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_user_email')
        ]
        
        indexes = [
            models.Index(fields=['user_id'], name='idx_user_id'),
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['created_at'], name='idx_user_created_at'),
            models.Index(fields=['updated_at'], name='idx_user_updated_at'),
        ]
        
    def __str__(self):
        return f'Name:{self.first_name} {self.last_name}, Email:{self.email}'    
