from django import forms
from .models import User   

# This form handles the creation of new user accounts in my system
class SignUpForm(forms.ModelForm):
    # Custom password fields so I can collect and confirm passwords securely
    # Referenced from - https://stackoverflow.com/questions/34609830/django-modelform-how-to-add-a-confirm-password-field
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Create a password"})
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"placeholder": "Re-enter your password"})
    )

    # The Meta class tells Django which model this form is linked to
    class Meta:
        model = User  # connects the form to my custom User model
        # use "delis" (ManyToManyField) no more "deli_id"
        fields = ["email", "role", "delis"]  # these fields come from the User model
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),  # adds a placeholder for the email box
        }

    # This function checks if the email is already registered.
    # Referenced from - https://stackoverflow.com/questions/36420733/form-validation-in-django-for-checking-unique-emails
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    # This function compares the two password fields to make sure they match. I had done this in past project
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password_confirm")
        if p1 and p2 and p1 != p2:
            self.add_error("password_confirm", "Passwords do not match.")
        return cleaned

    # This function saves the user after validating the data
    def save(self, commit=True):
        # I’m using Django’s built-in create_user method so the password is properly hashed
        user = User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            role=self.cleaned_data.get("role") or "staff",  # assigns 'staff' by default if no role selected
        )

        # Handle the many-to-many delis relation
        delis = self.cleaned_data.get("delis")
        if delis:
            user.delis.set(delis)

        return user
