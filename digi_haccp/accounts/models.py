from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom user manager that handles how users and superusers are created
class UserManager(BaseUserManager):
    # This function creates a regular user
    def create_user(self, email, password=None, role='staff', deli_id=None):
        if not email:
            raise ValueError("Users must have an email address")
        # Normalize and store the email, assign role and deli_id
        user = self.model(email=self.normalize_email(email), role=role, deli_id=deli_id)
        # The password is hashed using Django’s built-in method
        user.set_password(password)
        user.save(using=self._db)
        return user

    # This function creates an admin (superuser) account
    def create_superuser(self, email, password, role='manager', deli_id=None):
        # It calls create_user first, then gives admin privileges
        user = self.create_user(email, password=password, role=role, deli_id=deli_id)
        user.is_admin = True
        user.save(using=self._db)
        return user


# I made a user model for the Digi HACCP system
class User(AbstractBaseUser):
    # Each user logs in with an email instead of a username
    email = models.EmailField(unique=True)
    # Password field is handled securely through Django’s built-in system
    password = models.CharField(max_length=128)
    # Role helps me separate staff from managers
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('staff', 'Staff')])
    # For the time being, Optional deli ID so I can link users to their specific deli location
    deli_id = models.IntegerField(null=True, blank=True)

    # These fields handle user activity and admin rights
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # Connect this model to the custom user manager defined above
    objects = UserManager()

    # This tells Django to use email as the unique identifier for login
    USERNAME_FIELD = 'email'
    # No extra fields are required besides email and password
    REQUIRED_FIELDS = []

    # Returns the user’s email when printed or shown in admin panels
    def __str__(self):
        return self.email
