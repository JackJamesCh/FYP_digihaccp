from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .newuser import SignUpForm
from .forms import DeliForm, AssignDeliForm, ChecklistForm, ChecklistItem
from datetime import date, datetime

from .models import (
    Deli,
    User,
    Checklist,
    ChecklistInstance,
    ChecklistInstanceItem,
    ChecklistResponse,
    ResponseItem,
    TemplateField,
)
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.timezone import now, localdate
from decimal import Decimal, InvalidOperation
import json


# I wrote this view to handle the entire login process using Django's built-in authentication system. Reference:https://docs.djangoproject.com/en/5.0/topics/auth/default/#django.contrib.auth.authenticate
def login_view(request):
    if request.method == "POST":
        # I grab the email and password directly from the POST data that the user submitted
        email = request.POST['email']
        password = request.POST['password']

        # Here I use Django's authenticate() to check if the email/password match a user this function checks the user model and hashed password behind the scenes.
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # If authentication works, I log the user in with Django's login() helper. Reference: https://docs.djangoproject.com/en/5.0/topics/auth/default/#django.contrib.auth.login
            login(request, user)

            # After logging in I send the user to a different dashboard depending on their role
            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('dashboard')
        else:
            # If the credentials are wrong I show an error message using Django messages Reference: https://docs.djangoproject.com/en/5.0/ref/contrib/messages/
            messages.error(request, "Invalid email or password")

    # If it's a GET request or if login failed I just show the login template
    return render(request, 'accounts/login.html')


# This is the main dashboard for normal staff users. I protected this view using login_required so only authenticated users can see it.
@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


# This is the dashboard for managers. I wanted only users with role "manager" to access this.
# I manually check the user role here. If they aren't a manager, I send them back to the staff dashboard.
# If they are a manager, I show the manager dashboard template

@login_required(login_url='login')
def manager_dashboard_view(request):
    if request.user.role != 'manager':
        return redirect('dashboard')
    return render(request, 'accounts/manager_dashboard.html')


# I made this view to handle logging users out of the system.
def logout_view(request):
    logout(request)
    return redirect('login')


# This view handles user registration (sign-up). I built it using a custom SignUpForm that extends Django's user creation logic.
# If a user is already logged in, I don't want them signing up again so I send them back to the dashboard.
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        # I bind the form to the POST data the user submitted
        form = SignUpForm(request.POST)

        # If the form is valid, I create the user
        if form.is_valid():
            # Save the user to the database using the form's save() method
            user = form.save()

            # Right after creating the user, I try to log them in automatically
            logged_in_user = authenticate(
                request,
                email=user.email,
                password=form.cleaned_data["password"]
            )
            if logged_in_user:
                login(request, logged_in_user)
                messages.success(request, "Account created. Welcome!")
                return redirect('dashboard')

            # If for some reason auto-login fails, I still tell them the account was created
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        # For GET requests, I just show an empty sign-up form
        form = SignUpForm()

    # I render the signup page and pass the form so it can be displayed and validated in the template
    return render(request, 'accounts/signup.html', {"form": form})


# I created this helper function so I could reuse the "is manager" logic in decorators.
# It checks if a user is both authenticated and has role == "manager". Reference: https://stackoverflow.com/questions/8082670/django-user-passes-test-decorator
def is_manager(user):
    return user.is_authenticated and user.role == 'manager'


# This view allows a manager to see and manage all users. I used @user_passes_test with my is_manager helper so only managers can access it.
@user_passes_test(is_manager, login_url='dashboard')
def manage_users_view(request):
    users = User.objects.all().order_by('email')
    return render(request, 'accounts/manage_users.html', {'users': users})


# This view lets managers delete users. I again protect it with @user_passes_test so only managers can trigger deletions.
@user_passes_test(is_manager, login_url='dashboard')
def delete_user_view(request, user_id):
    try:
        # I fetch the user by their ID; if they don't exist, this will raise DoesNotExist
        user = User.objects.get(id=user_id)

        # I don't want managers deleting other managers, so I block that case
        if user.role == 'manager':
            messages.error(request, "You cannot delete another manager.")
        else:
            # If the user is not a manager you can delete them
            user.delete()
            messages.success(request, f"{user.email} has been deleted successfully.")
    except User.DoesNotExist:
        # If the user ID isn't found I show an error
        messages.error(request, "User not found.")
    # After handling deletion I go back to manage users
    return redirect('manage_users')


# This view lets managers see and manage all delis in the system.
@user_passes_test(is_manager, login_url='dashboard')
def manage_delis_view(request):
    delis = Deli.objects.all().order_by('deli_name')
    return render(request, 'accounts/manage_delis.html', {'delis': delis})


# This view is used for both creating a new deli and editing an existing one. I did this by making deli_id optional and reusing the same form.
# Reference ModelForm pattern: https://www.geeksforgeeks.org/python/django-modelform-create-form-from-models/
@user_passes_test(is_manager, login_url='dashboard')
def deli_form_view(request, deli_id=None):
    # If deli_id is provided I'm editing an existing deli. Otherwise I'm creating a brand new deli
    if deli_id:
        deli = Deli.objects.get(pk=deli_id)
        form = DeliForm(instance=deli)
        title = "Edit Deli"
    else:
        deli = None
        form = DeliForm()
        title = "Add New Deli"

    # If the request is POST I process the form submission
    if request.method == "POST":
        form = DeliForm(request.POST, instance=deli)
        if form.is_valid():
            form.save()
            if deli_id:
                messages.success(request, "Deli updated successfully.")
            else:
                messages.success(request, "New deli created successfully.")
            return redirect('manage_delis')

    # For GET requests or invalid POST I render the form page with the current form
    return render(request, 'accounts/deli_form.html', {'form': form, 'title': title})


# This view lets a manager delete a deli. I try to grab the deli by its primary key. If it doesn't exist, I show an error
@user_passes_test(is_manager, login_url='dashboard')
def delete_deli_view(request, deli_id):
    try:
        deli = Deli.objects.get(pk=deli_id)
        deli.delete()
        messages.success(request, "Deli deleted successfully.")
    except Deli.DoesNotExist:
        messages.error(request, "Deli not found.")
    return redirect('manage_delis')


# This view allows a manager to assign one or more delis to a user. First I get the user I want to assign delis to
# I bind the form to the POST data and tie it to the user instance. Saving the form updates the user's deli assignments
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
        # For GET I just show the form with current assignments pre-filled
        form = AssignDeliForm(instance=user)

    # I show the template that lets me assign delis to the user
    return render(request, 'accounts/assign_delis.html', {'form': form, 'user': user})


# This view lets a manager create a checklist and its items in bulk. I built this using a custom ChecklistForm and a "pasted items" textarea.
# Reference: https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django/Forms
@login_required
def create_checklist(request):
    if request.user.role != "manager":
        return redirect("dashboard")

    if request.method == "POST":
        form = ChecklistForm(request.POST, user=request.user)

        if form.is_valid():
            # I first save the checklist itself without committing related items yet
            checklist = form.save(commit=False)
            checklist.created_by = request.user
            checklist.save()

            # I convert each line from the "items_bulk" textarea into a ChecklistItem. I strip empty lines so only real item names are used
            # I use an order counter so items appear in the same order they were pasted

            pasted_items = form.cleaned_data.get("items_bulk", "")
            lines = [line.strip() for line in pasted_items.split("\n") if line.strip()]
            order = 1
            for line in lines:
                name = line
                chemical_used = ""
                if "|" in line:
                    name_part, chemical_part = line.split("|", 1)
                    name = name_part.strip()
                    chemical_used = chemical_part.strip()

                ChecklistItem.objects.create(
                    checklist=checklist,
                    name=name,
                    chemical_used=chemical_used,
                    order=order,
                )
                order += 1

            # After creating the checklist and items I send the user to a simple success page
            return redirect("checklist_success")
        
    else:
        form = ChecklistForm(user=request.user)

    return render(request, "accounts/create_checklist.html", {"form": form})


# I made this view to show a confirmation page after successfully creating a checklist.
def checklist_success(request):
    return render(request, "accounts/checklist_success.html")


# This view returns JSON data for a specific checklist, so the frontend can render column definitions and row data.
# Reference: https://www.youtube.com/watch?v=t8cGU5mS3m4
def api_get_checklist_data(request, pk):
    # I fetch the checklist or show a 404 if it doesn't exist
    checklist = get_object_or_404(Checklist, pk=pk)
    template_fields = checklist.template.fields.order_by("order")
    items = checklist.items.order_by("order")

    # I start with a base column for the item name
    column_defs = [{"headerName": "Item Name", "field": "item_name"}]

    # Then I add a column for each template field.
    for field in template_fields:
        column_defs.append({
            "headerName": field.label,
            "field": field.name,
        })

    # Now I build the row data, with one row per checklist item
    row_data = []
    for i in items:
        # Each row starts with the item name
        row = {"item_name": i.name}
        # For each template field, I start with an empty value to be filled later
        for field in template_fields:
            if field.name == "chemical_used":
                row[field.name] = i.chemical_used
            else:
                row[field.name] = ""
        row_data.append(row)

    # Finally, I return all this as JSON so the frontend can render a dynamic grid.
    return JsonResponse({
        "title": checklist.title,
        "template": checklist.template.name,
        "deli": checklist.deli.deli_name,
        "frequency": checklist.frequency,
        "columnDefs": column_defs,
        "rowData": row_data
    })


# This view lets managers see all checklists across the delis they are assigned to.
@login_required
def manager_checklists_combined(request):
    if request.user.role != "manager":
        return redirect("dashboard")

    # I get all delis assigned to the current manager
    delis = request.user.delis.all()

    # Then I find all checklists for those delis, newest first
    checklists = Checklist.objects.filter(deli__in=delis).order_by("-created_at")

    return render(request, "accounts/manager_checklists_combined.html", {
        "checklists": checklists,
    })


# This view lets a manager unassign a checklist from a deli without deleting history.
# I treat unassign as setting the checklist inactive so staff no longer see it.
@login_required
def manager_unassign_checklist(request, checklist_id):
    if request.user.role != "manager":
        return redirect("dashboard")

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    checklist = get_object_or_404(Checklist, id=checklist_id)

    # Managers can only modify checklists for delis assigned to them.
    if checklist.deli not in request.user.delis.all():
        messages.error(request, "You cannot modify a checklist for an unassigned deli.")
        return redirect("manager_checklists_combined")

    checklist.is_active = False
    checklist.save(update_fields=["is_active"])
    messages.success(request, f"Checklist '{checklist.title or checklist.template.name}' has been unassigned.")
    return redirect("manager_checklists_combined")


# This view allows a manager to fully delete a checklist assignment.
# Deleting removes checklist items, instances and related responses through cascades.
@login_required
def manager_delete_checklist(request, checklist_id):
    if request.user.role != "manager":
        return redirect("dashboard")

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    checklist = get_object_or_404(Checklist, id=checklist_id)

    if checklist.deli not in request.user.delis.all():
        messages.error(request, "You cannot delete a checklist for an unassigned deli.")
        return redirect("manager_checklists_combined")

    checklist_label = checklist.title or checklist.template.name
    checklist.delete()
    messages.success(request, f"Checklist '{checklist_label}' has been deleted.")
    return redirect("manager_checklists_combined")


# This view is for staff users to see the checklists they need to fill in.
# It also auto-creates daily instances of checklists if they don't exist for today.
@login_required
def staff_view_checklists(request):
    # I only want staff to access this; managers shouldn't fill staff checklists here
    if request.user.role != "staff":
        return redirect("dashboard")

    # I get all delis assigned to the current staff user
    delis = request.user.delis.all()

    # I use Python's date.today() to know which day's instance to use
    today = date.today()

    # I find all active checklists assigned to any of the user's delis
    checklists = Checklist.objects.filter(
        deli__in=delis,
        is_active=True
    )

    instances = []

    # For each checklist, I either find or create a ChecklistInstance for today
    # I used get_or_create here to avoid duplicates:
    # Reference: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#get-or-create
    for checklist in checklists:
        instance, created = ChecklistInstance.objects.get_or_create(
            checklist=checklist,
            deli=checklist.deli,
            date=today,
            defaults={"is_locked": False}
        )

        # If I just created this instance today I also create the row items
        if created:
            for item in checklist.items.all():
                ChecklistInstanceItem.objects.create(
                    instance=instance,
                    checklist_item=item
                )

        instances.append(instance)

    # I render a template that shows all today's instances for the staff user
    return render(request, "accounts/staff_checklists.html", {
        "instances": instances,
        "today": today
    })


# This view renders the actual "fill checklist" page building up a JSON structure
# for columns and rows that the frontend can use.
@login_required
def fill_checklist_view(request, instance_id):
    # I get the checklist instance or return 404 if it's missing
    instance = get_object_or_404(ChecklistInstance, pk=instance_id)

    # I make sure the current user is actually assigned to this deli
    if instance.deli not in request.user.delis.all():
        return redirect("dashboard")

    locked = instance.is_locked

    # GET OR CREATE SHARED RESPONSE (latest / last updated)
    response_qs = ChecklistResponse.objects.filter(
        checklist=instance.checklist,
        deli=instance.deli,
    )

    # For daily checklists only use today's response set
    if instance.checklist.frequency == "daily":
        response_qs = response_qs.filter(completed_at__date=localdate())

    # Pick the most recently updated response
    response = response_qs.order_by("-updated_at", "-completed_at").first()

    # If nothing exists yet create the first shared response
    if not response:
        response = ChecklistResponse.objects.create(
            checklist=instance.checklist,
            deli=instance.deli,
            completed_by=request.user,  # “created by” the first staff who opens it
        )

    # BUILD GRID DATA
    # I fetch all fields for the checklist template and items for the checklist itself
    fields = instance.checklist.template.fields.order_by("order")
    items = instance.checklist.items.order_by("order")

    # row_data will become a list of dicts, each representing a row in the grid
    row_data = []
    for item in items:
        row = {
            "item_id": item.id,
            "item_name": item.name,
        }

        # For each template field, I either get or create a ResponseItem
        # This pattern lets me ensure there is always a ResponseItem row ready for saving.
        for field in fields:
            answer, _ = ResponseItem.objects.get_or_create(
                response=response,
                checklist_item=item,
                template_field=field
            )

            # I convert the answer into a basic value that can be safely JSON-encoded
            value = None
            if field.field_type == "text":
                value = answer.answer_text
            elif field.field_type == "date":
                value = answer.answer_date.isoformat() if answer.answer_date else ""
            elif field.field_type == "time":
                value = answer.answer_time.strftime("%H:%M") if answer.answer_time else ""
            elif field.field_type == "datetime":
                value = answer.answer_datetime.isoformat() if answer.answer_datetime else ""
            elif field.field_type == "decimal":
                value = float(answer.answer_decimal) if answer.answer_decimal else ""
            elif field.field_type == "number":
                value = answer.answer_number if answer.answer_number is not None else ""
            elif field.field_type == "boolean":
                value = bool(answer.answer_boolean)

            if field.name == "chemical_used":
                value = item.chemical_used

            row[field.name] = value

        row_data.append(row)

    # COLUMN DEFINITIONS
    # I start with a non-editable "Item" column that shows the name of the checklist item
    col_defs = [{
        "headerName": "Item",
        "field": "item_name",
        "editable": False,
    }]

    # For each template field, I create a column that is editable unless the instance is locked
    for field in fields:
        is_editable = not locked
        if field.name == "chemical_used":
            is_editable = False

        col_defs.append({
            "headerName": field.label,
            "field": field.name,
            "editable": is_editable,
            "fieldType": field.field_type,
        })

    # RETURN JSON SAFELY TO TEMPLATE
    # I pass the column and row definitions as JSON strings so the JS on the template can read them.
    # Reference: https://docs.djangoproject.com/en/5.2/topics/serialization/#id2
    return render(request, "accounts/fill_checklist.html", {
        "instance": instance,
        "column_defs_json": json.dumps(col_defs),
        "row_data_json": json.dumps(row_data),
        "locked": locked,
        "response_id": response.id,
    })


# This view is used by the frontend to save a single field value when the user edits a cell in the grid.
@login_required
def api_save_field(request):
    if request.method != "POST":
        # I only accept POST here; other methods get a 405 error
        return JsonResponse({"error": "Invalid method"}, status=405)

    # I pull all the data I need from the POST request
    response_id = request.POST.get("response_id")
    item_id = request.POST.get("item_id")
    field_name = request.POST.get("field")
    value = request.POST.get("value")

    # I use get_object_or_404 to ensure these related objects exist or return a 404
    response = get_object_or_404(ChecklistResponse, id=response_id)
    item = get_object_or_404(ChecklistItem, id=item_id)
    template_field = get_object_or_404(
        TemplateField,
        template=response.checklist.template,
        name=field_name
    )

    # I look up the existing ResponseItem row that matches the response item and template field
    answer = ResponseItem.objects.get(
        response=response,
        checklist_item=item,
        template_field=template_field
    )

    # Prevent edits to read-only fields
    if template_field.name == "chemical_used":
        return JsonResponse({"error": "Chemical Used is read-only."}, status=400)

    # I now update the correct field on the ResponseItem based on the field type.
    # This is a common pattern when handling dynamic form-like data.
    if template_field.field_type == "text":
        answer.answer_text = value
    elif template_field.field_type == "date":
        if value:
            try:
                parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

            if template_field.name == "use_by_date" and parsed_date < localdate():
                return JsonResponse({"error": "Use-by date cannot be in the past."}, status=400)

            answer.answer_date = parsed_date
        else:
            answer.answer_date = None
    elif template_field.field_type == "datetime":
        answer.answer_datetime = value or None
    elif template_field.field_type == "time":
        # Expect "HH:MM" Reference: https://www.geeksforgeeks.org/python/convert-datetime-string-to-yyyy-mm-dd-hhmmss-format-in-python/
        if value:
            try:
                answer.answer_time = datetime.strptime(value, "%H:%M").time()
            except ValueError:
                return JsonResponse({"error": "Invalid time format. Use HH:MM"}, status=400)
        else:
            answer.answer_time = None
    elif template_field.field_type == "decimal":
        if value:
            try:
                decimal_value = Decimal(value)
            except InvalidOperation:
                return JsonResponse({"error": "Please enter a valid number."}, status=400)

            if template_field.name == "core_temp":
                if decimal_value < Decimal("75") or decimal_value > Decimal("100"):
                    return JsonResponse(
                        {"error": "Core temperature must be between 75 and 100."},
                        status=400
                    )

            answer.answer_decimal = decimal_value
        else:
            answer.answer_decimal = None
    elif template_field.field_type == "number":
        if value:
            try:
                number_value = int(value)
            except ValueError:
                return JsonResponse({"error": "Please enter a whole number."}, status=400)

            if template_field.name == "core_temp":
                if number_value < 75 or number_value > 100:
                    return JsonResponse(
                        {"error": "Core temperature must be between 75 and 100."},
                        status=400
                    )

            answer.answer_number = number_value
        else:
            answer.answer_number = None
    elif template_field.field_type == "boolean":
        answer.answer_boolean = (value.lower() == "true")

    answer.last_edited_by = request.user
    answer.last_edited_at = now()

    # After updating I save the object to persist the changes
    answer.save()
    response.save(update_fields=["updated_at"])  # the "latest" timestamp


    # I return a simple JSON success response
    return JsonResponse({"success": True})


# This view lets a manager see the full checklist history for a specific deli.
@login_required
def deli_checklist_history(request, deli_id):
    if request.user.role != "manager":
        return redirect("dashboard")

    # I use deli_ID instead of pk here based on how the model was defined
    deli = get_object_or_404(Deli, deli_ID=deli_id)

    # I also make sure the manager actually has access to this deli
    if deli not in request.user.delis.all():
        return redirect("manager_dashboard")

    # I fetch all instances for this deli ordered from newest date to oldest
    instances = ChecklistInstance.objects.filter(
        deli=deli
    ).order_by("-date", "-created_at")

    return render(request, "accounts/manager_deli_checklists.html", {
        "deli": deli,
        "instances": instances
    })


# This API view returns the detailed grid data for a specific checklist instance,
# so managers can see what staff filled in on that day.
@login_required
def api_manager_instance_detail(request, instance_id):
    # I get the instance or show 404 if it doesn't exist
    instance = get_object_or_404(ChecklistInstance, id=instance_id)

    # I collect the checklist its fields and items to build the grid structure
    checklist = instance.checklist
    fields = checklist.template.fields.order_by("order")
    items = checklist.items.order_by("order")

    # I find responses completed for this checklist in this deli on that specific date
    responses = ChecklistResponse.objects.filter(
        checklist=checklist,
        deli=instance.deli,
        completed_at__date=instance.date
    )

    # For now I just take the first response (assuming one per checklist per day)
    response = responses.order_by("-updated_at", "-completed_at").first()

    edited_users = User.objects.filter(
        edited_response_items__response=response
    ).distinct()

    # collect staff involved: starter + anyone who edited any cell
    staff_emails = set()

    # starter (who created the response)
    if response.completed_by_id:
        staff_emails.add(response.completed_by.email)

    # editors (who changed any cell)
    edited_emails = ResponseItem.objects.filter(
        response=response,
        last_edited_by__isnull=False
    ).values_list("last_edited_by__email", flat=True).distinct()

    staff_emails.update(edited_emails)

    staff_list = sorted(staff_emails)

    # If there is no response I just return empty structures
    if not responses.exists():
        return JsonResponse({"columnDefs": [], "rowData": []})

    # I now build the row data for the grid
    row_data = []
    for item in items:
        row = {
            "item_name": item.name
        }
        for field in fields:
            try:
                # I try to find the ResponseItem for this item plus field
                answer = ResponseItem.objects.get(
                    response=response,
                    checklist_item=item,
                    template_field=field
                )
                # I pick whichever of the answer fields is not None. This works because only one of them should be used depending on field_type.
                value = (
                    answer.answer_text or
                    answer.answer_date or
                    (answer.answer_time.strftime("%H:%M") if answer.answer_time else None) or
                    answer.answer_datetime or
                    answer.answer_decimal or
                    answer.answer_number or
                    answer.answer_boolean
                )
            except ResponseItem.DoesNotExist:
                # If there is no response for that item/field I just leave it empty
                value = ""

            if field.name == "chemical_used":
                value = item.chemical_used

            row[field.name] = value
        row_data.append(row)

    # I also build the column definitions: one for item name plus one for each template field
    col_defs = [{"headerName": "Item", "field": "item_name"}]
    for field in fields:
        col_defs.append({
            "headerName": field.label,
            "field": field.name,
            "editable": False,
        })

    # I return all the grid data plus extra info (who filled it and when)
    # Reference: https://docs.python.org/3/library/datetime.html#datetime.date.strftime
    return JsonResponse({
        "columnDefs": col_defs,
        "rowData": row_data,
        "filled_by": response.completed_by.email,
        "filled_time": response.completed_at.strftime("%d %b %Y, %H:%M"),
        "staff_involved": staff_list,
    })
