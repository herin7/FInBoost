from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser

# Create your models here.

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('user', 'User'), ('admin', 'Admin')], default='user')

    def __str__(self):
        return self.username
    
