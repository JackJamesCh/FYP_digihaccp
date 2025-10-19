from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def base_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', base_redirect, name='base_redirect'),
    path('', include('accounts.urls')),
]
