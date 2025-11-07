from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .newuser import SignUpForm
from .forms import DeliForm, AssignDeliForm
from .models import Deli, User
from django.contrib.auth.decorators import user_passes_test

# Handles the login process
# I made this function to handle logging users into the system using their email and password.
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # This checks if the email and password match a valid user in the database
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # If authentication succeeds, log the user in
            login(request, user)

            # Redirect users based on their role
            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('dashboard')
        else:
            # Show an error message if credentials are wrong
            messages.error(request, "Invalid email or password")

    # If it's a GET request, it just displays the login page
    return render(request, 'accounts/login.html')

# Dashboard for staff
# I made this view for normal staff users once they log in.
@login_required(login_url='login')
def dashboard_view(request):
    # Renders the staff dashboard and passes in user data
    return render(request, 'accounts/dashboard.html')

# Dashboard for managers
# Only managers should be able to see this page.
@login_required(login_url='login')
def manager_dashboard_view(request):
    if request.user.role != 'manager':
        # If someone without the manager role tries to access this, send them back to staff dashboard
        return redirect('dashboard')
    return render(request, 'accounts/manager_dashboard.html')

# Handles user logout
# This function logs users out of the system.
def logout_view(request):
    logout(request)
    return redirect('login')

# Handles user registration (Sign-Up)
# This view lets new users register for an account.
def signup_view(request):
    # If the user is already logged in, they shouldn’t see the signup page
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = SignUpForm(request.POST)

        # Check if all form data is valid
        if form.is_valid():
            # Save new user in the database
            user = form.save()

            # Automatically log in the new user after signing up
            logged_in_user = authenticate(request, email=user.email, password=form.cleaned_data["password"])
            if logged_in_user:
                login(request, logged_in_user)
                messages.success(request, "Account created. Welcome!")
                return redirect('dashboard')

            # If automatic login fails, they can log in manually
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        # If it’s not a POST request, show a blank signup form
        form = SignUpForm()

    # Render the signup page with the signup form
    return render(request, 'accounts/signup.html', {"form": form})

# Manager-only helper
# I created this helper function so only managers can access certain views.
def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

# View to manage all users (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def manage_users_view(request):
    # This pulls all users from the database, sorted by email
    users = User.objects.all().order_by('email')
    return render(request, 'accounts/manage_users.html', {'users': users})

# View to delete users (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        # Prevent managers from deleting other managers
        if user.role == 'manager':
            messages.error(request, "You cannot delete another manager.")
        else:
            user.delete()
            messages.success(request, f"{user.email} has been deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect('manage_users')

# View to list all delis (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def manage_delis_view(request):
    # Pulls all delis from the database and displays them
    delis = Deli.objects.all().order_by('deli_name')
    return render(request, 'accounts/manage_delis.html', {'delis': delis})

# View to create or edit a deli (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def deli_form_view(request, deli_id=None):
    # If an ID is passed, the manager is editing a deli
    if deli_id:
        deli = Deli.objects.get(pk=deli_id)
        form = DeliForm(instance=deli)
        title = "Edit Deli"
    else:
        # Otherwise, they’re adding a new one
        deli = None
        form = DeliForm()
        title = "Add New Deli"

    # Handles the form submission
    if request.method == "POST":
        form = DeliForm(request.POST, instance=deli)
        if form.is_valid():
            form.save()
            if deli_id:
                messages.success(request, "Deli updated successfully.")
            else:
                messages.success(request, "New deli created successfully.")
            return redirect('manage_delis')

    # Render the form page
    return render(request, 'accounts/deli_form.html', {'form': form, 'title': title})

# View to delete a deli (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def delete_deli_view(request, deli_id):
    try:
        deli = Deli.objects.get(pk=deli_id)
        deli.delete()
        messages.success(request, "Deli deleted successfully.")
    except Deli.DoesNotExist:
        messages.error(request, "Deli not found.")
    return redirect('manage_delis')

# Assign delis to users (Manager only)
@user_passes_test(is_manager, login_url='dashboard')
def assign_delis_view(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        form = AssignDeliForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.email} deli assignments updated successfully.")
            return redirect('manage_users')
    else:
        form = AssignDeliForm(instance=user)

    # Renders the assign delis form
    return render(request, 'accounts/assign_delis.html', {'form': form, 'user': user})
