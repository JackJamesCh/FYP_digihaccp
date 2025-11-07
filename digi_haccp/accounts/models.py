from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# (Custom User Manager)
# I created my own user manager to handle user creation logic instead of using Django’s default.
# This allows me to use email as the main login field instead of a username.
class UserManager(BaseUserManager):
    # This function creates a normal user (like a staff account)
    def create_user(self, email, password=None, role='staff'):
        if not email:
            raise ValueError("Users must have an email address")  # Just to make sure every user has an email
        user = self.model(email=self.normalize_email(email), role=role)  # Normalize makes the email lowercase
        user.set_password(password)  # This securely hashes the password
        user.save(using=self._db)  # Saves the user to the database
        return user

    # This function creates a superuser (a manager)
    def create_superuser(self, email, password, role='manager'):
        user = self.create_user(email, password=password, role=role)
        user.is_admin = True  # Gives admin high-level permissions
        user.save(using=self._db)
        return user

# (Deli model)
# This model represents a Deli store. Each deli has an ID, name, address, and phone number.
class Deli(models.Model):
    deli_ID = models.AutoField(primary_key=True)  # Auto-generated ID for each deli
    deli_name = models.CharField(max_length=100)  # Name of the deli
    address = models.CharField(max_length=255)  # Address field for location info
    phone_number = models.IntegerField()  # Stores the deli’s contact number

    def __str__(self):
        return self.deli_name  # This helps display the deli name in the admin panel

# User model (many-to-many to Deli)
# I built a custom user model so I could use email for login instead of the default username.
# Each user can be linked to multiple delis (and vice versa).
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)  # This replaces the username as the login field
    password = models.CharField(max_length=128)  # Django will hash this when saved
    role = models.CharField(
        max_length=20,
        choices=[('manager', 'Manager'), ('staff', 'Staff')]  # Role options
    )

    # Many-to-Many link: one user can belong to multiple delis, and one deli can have multiple users
    delis = models.ManyToManyField(Deli, related_name='users', blank=True)

    is_active = models.BooleanField(default=True)  # Whether the account is active
    is_admin = models.BooleanField(default=False)  # Whether the user is an admin

    objects = UserManager()  # This connects the custom manager I made above

    USERNAME_FIELD = 'email'  # Tells Django to use email for authentication
    REQUIRED_FIELDS = []  # No extra required fields for superusers besides email and password

    def __str__(self):
        return self.email  # Displays the email when referring to a user object
