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



#  EXTENSIBLE CHECKLIST SYSTEM

# (Checklist Template)
# I created this model so the system can support different types of checklist formats.
# Each template represents a “type” of checklist like Food Safety or Cleaning.
class ChecklistTemplate(models.Model):
    """
    Defines a *type* of checklist.
    Example: Food Safety Checklist, Cleaning Checklist, Delivery Log, etc.
    The app creates these templates; managers cannot edit them.
    """
    code = models.CharField(max_length=50, unique=True)   # internal id, e.g. "FOOD_SAFETY"
    name = models.CharField(max_length=100)               # visible name
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# (Template Field)
# I made this so each template can have flexible types of questions.
# For example: text fields, dates, numbers and yes/no answers.
class TemplateField(models.Model):
    """
    Defines a field inside a template (dynamic field structure).
    Example: For Food Safety template:
        - food_name (text)
        - use_by_date (date)
        - country_of_origin (text)
        - core_temp (decimal)
        - corrective_action (text)
        - prepared_time (datetime)
    """

    FIELD_TYPES = [
        ('text', 'Text'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date & Time'),
        ('decimal', 'Decimal Number'),
        ('number', 'Whole Number'),
        ('boolean', 'Yes/No'),
    ]

    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name="fields")
    name = models.CharField(max_length=100)      # internal name
    label = models.CharField(max_length=255)     # human readable label
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)   # ordering of fields

    def __str__(self):
        return f"{self.template.name}: {self.label}"


# (Checklist Model)
# This represents a single checklist created by a manager for a specific deli.
# I used a template so the structure of the checklist is dynamic and reusable.
class Checklist(models.Model):
    """
    A single checklist created by a manager for a deli and date.
    Example:
        Food Safety Checklist for Deli X on 12 Nov 2025
    """
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.PROTECT, related_name="checklists")
    deli = models.ForeignKey(Deli, on_delete=models.CASCADE, related_name="checklists")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_checklists")
    created_at = models.DateTimeField(auto_now_add=True)

    FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]

    frequency = models.CharField(max_length=20, choices=FREQUENCIES, default='daily')
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"{self.template.name} - {self.deli.deli_name} ({self.frequency})"


# (Checklist Item)
# These are the actual rows/questions inside a specific checklist.
# I added an order field so I can control the order the items appear in.
class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.checklist})"


# (Checklist Response)
# Whenever a staff member fills out a checklist, I save one ChecklistResponse instance.
# This lets me keep history of who filled what and when.
class ChecklistResponse(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="responses")
    deli = models.ForeignKey(Deli, on_delete=models.CASCADE)
    completed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checklist_responses")
    completed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ add this

    def __str__(self):
        return f"Response to {self.checklist} by {self.completed_by.email}"


# (Response Item)
# This stores a SINGLE answer to a SINGLE field on a SINGLE checklist item.
# I made this flexible so it can store text, dates, numbers or yes/no.
class ResponseItem(models.Model):
    """
    Stores a SINGLE answer to a SINGLE template field for a SINGLE checklist item,
    belonging to ONE checklist response session.
    """

    response = models.ForeignKey(
        'ChecklistResponse',
        on_delete=models.CASCADE,
        related_name="answers",
    )

    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE,
        related_name="responses"
    )

    template_field = models.ForeignKey(
        TemplateField,
        on_delete=models.PROTECT,
        related_name="responses"
    )

    # (Flexible Answer Fields)
    # I added different fields here so I can support all possible answer types
    # based on the template field (text, date, number, boolean, etc.)
    answer_text = models.TextField(null=True, blank=True)
    answer_date = models.DateField(null=True, blank=True)
    answer_datetime = models.DateTimeField(null=True, blank=True)
    answer_decimal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    answer_number = models.IntegerField(null=True, blank=True)
    answer_boolean = models.BooleanField(null=True, blank=True)
    answer_time = models.TimeField(null=True, blank=True)

    last_edited_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="edited_response_items"
    )
    last_edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.checklist_item} — {self.template_field.label}"


# (Checklist Instance)
# I created this so staff can fill a checklist repeatedly—for example once per day.
# Each instance represents the checklist for a specific date.
class ChecklistInstance(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="instances")
    deli = models.ForeignKey(Deli, on_delete=models.CASCADE)
    date = models.DateField()  # The day this instance is for
    is_locked = models.BooleanField(default=False)  # I lock an instance after staff complete it
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('checklist', 'deli', 'date')  # Prevent duplicates

    def __str__(self):
        return f"{self.checklist.title} — {self.deli} — {self.date}"

# (Checklist Instance Item)
# This connects a generated checklist instance to the actual checklist items.
# Staff will later fill answers for these items using ResponseItem.
class ChecklistInstanceItem(models.Model):
    instance = models.ForeignKey(
        ChecklistInstance, on_delete=models.CASCADE, related_name="items"
    )
    checklist_item = models.ForeignKey(
        ChecklistItem, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.instance} — {self.checklist_item}"
