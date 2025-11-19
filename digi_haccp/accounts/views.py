from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .newuser import SignUpForm
from .forms import DeliForm, AssignDeliForm, ChecklistForm, ChecklistItem
from datetime import date
from .models import Deli, User, Checklist, ChecklistInstance, ChecklistInstanceItem, ChecklistResponse, ResponseItem, TemplateField
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils.timezone import now, localdate
import json


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


@login_required
def create_checklist(request):
    if request.user.role != "manager":
        return redirect("dashboard")

    if request.method == "POST":
        form = ChecklistForm(request.POST)

        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.created_by = request.user
            checklist.save()

            # Convert textarea lines to checklist items
            pasted_items = form.cleaned_data.get("items_bulk", "")
            lines = [line.strip() for line in pasted_items.split("\n") if line.strip()]

            order = 1
            for line in lines:
                ChecklistItem.objects.create(
                    checklist=checklist,
                    name=line,
                    order=order
                )
                order += 1

            return redirect("checklist_success")

    else:
        form = ChecklistForm()

    return render(request, "accounts/create_checklist.html", {"form": form})


def checklist_success(request):
    return render(request, "accounts/checklist_success.html")


def api_get_checklist_data(request, pk):
    checklist = get_object_or_404(Checklist, pk=pk)
    template_fields = checklist.template.fields.order_by("order")
    items = checklist.items.order_by("order")

    column_defs = [{"headerName": "Item Name", "field": "item_name"}]

    for field in template_fields:
        column_defs.append({
            "headerName": field.label,
            "field": field.name,
        })

    row_data = []
    for i in items:
        row = {"item_name": i.name}
        for field in template_fields:
            row[field.name] = ""
        row_data.append(row)

    return JsonResponse({
        "title": checklist.title,
        "template": checklist.template.name,
        "deli": checklist.deli.deli_name,
        "frequency": checklist.frequency,
        "columnDefs": column_defs,
        "rowData": row_data
    })


@login_required
def manager_checklists_combined(request):
    if request.user.role != "manager":
        return redirect("dashboard")

    delis = request.user.delis.all()
    checklists = Checklist.objects.filter(deli__in=delis).order_by("-created_at")

    return render(request, "accounts/manager_checklists_combined.html", {
        "checklists": checklists,
    })


@login_required
def staff_view_checklists(request):
    # Only staff should access this
    if request.user.role != "staff":
        return redirect("dashboard")

    # All delis assigned to this user
    delis = request.user.delis.all()

    today = date.today()

    # All checklists assigned to user's delis
    checklists = Checklist.objects.filter(
        deli__in=delis,
        is_active=True
    )

    instances = []

    for checklist in checklists:
        # Check if a daily instance already exists
        instance, created = ChecklistInstance.objects.get_or_create(
            checklist=checklist,
            deli=checklist.deli,
            date=today,
            defaults={"is_locked": False}
        )

        # If created today → generate rows (ChecklistInstanceItem)
        if created:
            for item in checklist.items.all():
                ChecklistInstanceItem.objects.create(
                    instance=instance,
                    checklist_item=item
                )

        instances.append(instance)

    return render(request, "accounts/staff_checklists.html", {
        "instances": instances,
        "today": today
    })


@login_required
def fill_checklist_view(request, instance_id):
    instance = get_object_or_404(ChecklistInstance, pk=instance_id)

    # Ensure user belongs to this deli
    if instance.deli not in request.user.delis.all():
        return redirect("dashboard")

    locked = instance.is_locked

    # --- 1️⃣ GET OR CREATE RESPONSE ---
    # Fix: You cannot filter by completed_at__date inside get_or_create
    response_qs = ChecklistResponse.objects.filter(
        checklist=instance.checklist,
        deli=instance.deli,
        completed_by=request.user,
    )

    # Daily checklists: use today's response
    if instance.checklist.frequency == "daily":
        response_qs = response_qs.filter(completed_at__date=localdate())

    response = response_qs.first()
    if not response:
        response = ChecklistResponse.objects.create(
            checklist=instance.checklist,
            deli=instance.deli,
            completed_by=request.user
        )

    # --- 2️⃣ BUILD GRID DATA ---
    fields = instance.checklist.template.fields.order_by("order")
    items = instance.checklist.items.order_by("order")

    row_data = []
    for item in items:
        row = {
            "item_id": item.id,
            "item_name": item.name,
        }

        for field in fields:
            answer, _ = ResponseItem.objects.get_or_create(
                response=response,
                checklist_item=item,
                template_field=field
            )

            # push value into JSON table
            value = None
            if field.field_type == "text":
                value = answer.answer_text
            elif field.field_type == "date":
                value = answer.answer_date.isoformat() if answer.answer_date else ""
            elif field.field_type == "datetime":
                value = answer.answer_datetime.isoformat() if answer.answer_datetime else ""
            elif field.field_type == "decimal":
                value = float(answer.answer_decimal) if answer.answer_decimal else ""
            elif field.field_type == "number":
                value = answer.answer_number if answer.answer_number is not None else ""
            elif field.field_type == "boolean":
                value = bool(answer.answer_boolean)

            row[field.name] = value

        row_data.append(row)

    # --- 3️⃣ COLUMN DEFINITIONS ---
    col_defs = [{
        "headerName": "Item",
        "field": "item_name",
        "editable": False,
    }]

    for field in fields:
        col_defs.append({
            "headerName": field.label,
            "field": field.name,
            "editable": not locked,
        })

    # --- 4️⃣ RETURN JSON SAFELY TO TEMPLATE ---
    return render(request, "accounts/fill_checklist.html", {
        "instance": instance,
        "column_defs_json": json.dumps(col_defs),
        "row_data_json": json.dumps(row_data),
        "locked": locked,
        "response_id": response.id,
    })


@login_required
def api_save_field(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    response_id = request.POST.get("response_id")
    item_id = request.POST.get("item_id")
    field_name = request.POST.get("field")
    value = request.POST.get("value")

    response = get_object_or_404(ChecklistResponse, id=response_id)
    item = get_object_or_404(ChecklistItem, id=item_id)
    template_field = get_object_or_404(TemplateField, name=field_name)

    # Look up row
    answer = ResponseItem.objects.get(
        response=response,
        checklist_item=item,
        template_field=template_field
    )

    # Save based on field type
    if template_field.field_type == "text":
        answer.answer_text = value
    elif template_field.field_type == "date":
        answer.answer_date = value or None
    elif template_field.field_type == "datetime":
        answer.answer_datetime = value or None
    elif template_field.field_type == "decimal":
        answer.answer_decimal = value or None
    elif template_field.field_type == "number":
        answer.answer_number = int(value) if value else None
    elif template_field.field_type == "boolean":
        answer.answer_boolean = (value.lower() == "true")

    answer.save()

    return JsonResponse({"success": True})
