from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Create your models here.
class CustomUserManager(BaseUserManager):
 
    def create_user(self, email, password=None, **other_fields):
        user = self.model(email=email, **other_fields)
        if password:
            user.set_password(password)
        user.save()
        return user


    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('role', 'admin')  # Set the role to 'admin'        
        return self.create_user(email, password, **other_fields)
    
    
class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('agent', 'Agent'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='agent')

    objects = CustomUserManager()  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    username = models.CharField(max_length=150, blank=True, null=True)  # Make username optional

    

    def __str__(self):
        return self.email