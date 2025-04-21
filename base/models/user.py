from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone

from sebania.exceptions.common import UnknownErrorException
from sebania.utils import crypto_utils


# Create your models here.

class UserProfileManager(BaseUserManager):
    """ Manager for user profiles """
    def create_employe(self, email, first_name=None, last_name=None):
        employe_password = crypto_utils.generate_password()
        employe = self.create_user(password=employe_password, first_name=first_name, last_name=last_name, email=email)
        employe.add_to_group("EMPLOYE")

        return employe, employe_password

    def create_responsable(self, email, password=None, first_name=None, last_name=None):
        responsable = self.create_user(password=password, first_name=first_name, last_name=last_name, email=email)
        responsable.add_to_group("RESPONSABLE")

        return responsable

    def create_user(self, email, password=None, first_name=None, last_name=None):
        """ Create a new user profile """
        if not email:
            raise UnknownErrorException(ValueError('User must have an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=email, first_name=first_name, last_name=last_name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, first_name, last_name):
        """ Create a new superuser profile """
        user = self.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserProfileManager()

    def __str__(self):
        """ Return string representation of our user """
        return self.email

    def add_to_group(self, group_name: str):
        group = Group.objects.get(name=group_name)
        group.user_set.add(self)