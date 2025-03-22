from django.contrib.auth.base_user import BaseUserManager
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class UserProfileManager(BaseUserManager):
    """ Manager for user profiles """
    def create_user(self, email, password=None):
        """ Create a new user profile """
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create a new superuser profile """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user

class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserProfileManager()

    def __str__(self):
        """ Return string representation of our user """
        return self.email