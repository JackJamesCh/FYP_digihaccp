from django.urls import path
from . import views

# This file connects each webpage URL to the correct view function.
# It basically tells Django which part of the website to load when a user visits a specific link.

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('manager-dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('manage-delis/', views.manage_delis_view, name='manage_delis'),
    path('deli/new/', views.deli_form_view, name='new_deli'),
    path('deli/edit/<int:deli_id>/', views.deli_form_view, name='edit_deli'),
    path('deli/delete/<int:deli_id>/', views.delete_deli_view, name='delete_deli'),
    path('assign-delis/<int:user_id>/', views.assign_delis_view, name='assign_delis'),
    path("checklists/create/", views.create_checklist, name="create_checklist"),
    path("checklists/success/", views.checklist_success, name="checklist_success"),
]
