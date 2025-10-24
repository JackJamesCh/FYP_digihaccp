from django.urls import path
from . import views

# This file connects each webpage URL to the correct view function.
# It basically tells Django which part of the website to load when a user visits a specific link.

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

]
