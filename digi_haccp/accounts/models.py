from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# ----------------------------
# Custom User Manager
# ----------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='staff'):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, role='manager'):
        user = self.create_user(email, password=password, role=role)
        user.is_admin = True
        user.save(using=self._db)
        return user


# ----------------------------
# Deli model
# ----------------------------
class Deli(models.Model):
    deli_ID = models.AutoField(primary_key=True)
    deli_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.IntegerField()

    def __str__(self):
        return self.deli_name


# ----------------------------
# User model (many-to-many to Deli)
# ----------------------------
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('staff', 'Staff')])

    # ✅ Many-to-Many link
    delis = models.ManyToManyField(Deli, related_name='users', blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
