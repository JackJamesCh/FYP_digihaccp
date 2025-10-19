from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='staff', deli_id=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), role=role, deli_id=deli_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, role='manager', deli_id=None):
        user = self.create_user(email, password=password, role=role, deli_id=deli_id)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('staff', 'Staff')])
    deli_id = models.IntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
