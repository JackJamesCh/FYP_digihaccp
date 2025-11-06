from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .newuser import SignUpForm


# ----------------------------
# Handles the login process
# ----------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Check if the email and password match a user in the database
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # If authentication succeeds, log the user in
            login(request, user)

            # 🔹 Redirect based on user role
            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('dashboard')
        else:
            # If login fails, show an error message
            messages.error(request, "Invalid email or password")

    # If it’s a GET request, just show the login page
    return render(request, 'accounts/login.html')


# ----------------------------
# Dashboard for staff
# ----------------------------
@login_required(login_url='login')
def dashboard_view(request):
    # Renders the dashboard page with user information
    return render(request, 'accounts/dashboard.html')


# ----------------------------
# 🔹 Dashboard for managers
# ----------------------------
@login_required(login_url='login')
def manager_dashboard_view(request):
    # Allow only managers to access this page
    if request.user.role != 'manager':
        # If a staff tries to access, send them to normal dashboard
        return redirect('dashboard')

    # Render manager dashboard
    return render(request, 'accounts/manager_dashboard.html')


# ----------------------------
# Handles logging out users
# ----------------------------
def logout_view(request):
    # Logs the user out and redirects back to the login page
    logout(request)
    return redirect('login')


# ----------------------------
# Handles user registration (sign-up)
# ----------------------------
def signup_view(request):
    # If a logged-in user tries to access signup, redirect them to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # If the signup form was submitted
    if request.method == "POST":
        form = SignUpForm(request.POST)

        # Check if all fields are valid and the data passes form validation
        if form.is_valid():
            # Save the new user to the database
            user = form.save()

            # Automatically log the new user in after signup for a smoother experience
            logged_in_user = authenticate(request, email=user.email, password=form.cleaned_data["password"])
            if logged_in_user:
                login(request, logged_in_user)
                messages.success(request, "Account created. Welcome!")
                return redirect('dashboard')

            # If auto-login doesn’t work, prompt them to log in manually
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        # If it’s not a POST request, show an empty signup form
        form = SignUpForm()

    # Render the signup page and pass the form into the template
    return render(request, 'accounts/signup.html', {"form": form})

# ----------------------------
# 🔹 Manager-only user management
# ----------------------------
from django.contrib.auth.decorators import user_passes_test
from .models import User

# Helper: only allow managers
def is_manager(user):
    return user.is_authenticated and user.role == 'manager'


# ✅ View to list all users (only for managers)
@user_passes_test(is_manager, login_url='dashboard')
def manage_users_view(request):
    users = User.objects.all().order_by('email')  # fetch all users from DB
    return render(request, 'accounts/manage_users.html', {'users': users})


# ✅ View to delete a user (only for managers)
@user_passes_test(is_manager, login_url='dashboard')
def delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        # prevent deleting other managers
        if user.role == 'manager':
            messages.error(request, "You cannot delete another manager.")
        else:
            user.delete()
            messages.success(request, f"{user.email} has been deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect('manage_users')
