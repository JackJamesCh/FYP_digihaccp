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
    path("manager/checklists/", views.manager_checklists_combined, name="manager_checklists_combined"),
    path("manager/checklists/<int:checklist_id>/assign/", views.manager_assign_checklist, name="manager_assign_checklist"),
    path("manager/checklists/<int:checklist_id>/unassign/", views.manager_unassign_checklist, name="manager_unassign_checklist"),
    path("manager/checklists/<int:checklist_id>/delete/", views.manager_delete_checklist, name="manager_delete_checklist"),
    path("api/checklists/<int:pk>/", views.api_get_checklist_data, name="api_get_checklist_data"),
    path("staff/checklists/", views.staff_view_checklists, name="staff_checklists"),
    path("checklist/fill/<int:instance_id>/", views.fill_checklist_view, name="fill_checklist"),
    path("api/checklist/save/", views.api_save_field, name="api_save_field"),
    path("manager/deli/<int:deli_id>/checklists/", views.deli_checklist_history, name="deli_checklist_history"),
    path("manager/checklist/instance/<int:instance_id>/data/", views.api_manager_instance_detail, name="api_manager_instance_detail"),

]
