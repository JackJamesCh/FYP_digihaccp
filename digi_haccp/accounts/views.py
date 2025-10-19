from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password")
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')

