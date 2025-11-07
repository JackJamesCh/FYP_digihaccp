from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Base Redirect Function
# I made this function to control what happens when someone visits the home page ("/").
# If the user is already logged in, it sends them straight to their dashboard.
# If not logged in, they get redirected to the login page.
def base_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Logged-in users go to dashboard
    else:
        return redirect('login')  # Others go to login page

# URL Patterns
# This is where I connect all the routes in my Django project.
# It tells Django which views or apps should handle each path.
urlpatterns = [
    path('admin/', admin.site.urls),        # Gives access to Django’s built-in admin site
    path('', base_redirect, name='base_redirect'),  # Redirects home page to login or dashboard
    path('', include('accounts.urls')),     # Includes all URLs from my custom accounts app
]
