"""
Django settings for digi_haccp project.
Generated automatically when I created the project using 'django-admin startproject'.
This file controls how my whole Django app runs — including database setup,
installed apps, templates, and security configurations.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from the .env file for sensitive data like database credentials
load_dotenv()

# BASE_DIR defines the main directory path of my Django project
BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------
# SECURITY & DEBUG SETTINGS
# -----------------------------

# Secret key used for encryption and Django’s internal security features
SECRET_KEY = 'django-insecure-9u$s3b2(%d#x%*sgu=!*@x*5u-*%4@tb69e17=#vrrl&vsoti_'

# Debug mode helps me see detailed error messages during development
# (I’ll turn this off in production)
DEBUG = True

# Hosts that are allowed to access my app
ALLOWED_HOSTS = []


# -----------------------------
# APPLICATIONS
# -----------------------------

INSTALLED_APPS = [
    # My custom app for managing users and authentication
    'accounts',

    # Default Django apps that handle admin, authentication, sessions, and static files
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


# -----------------------------
# MIDDLEWARE
# -----------------------------
# Middleware controls the flow of requests and responses through the system.
# It handles things like security, sessions, and authentication automatically.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Protects against CSRF attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles user authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Manages flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -----------------------------
# URL & TEMPLATE CONFIGURATION
# -----------------------------

# Points Django to my main URL routing file
ROOT_URLCONF = 'digi_haccp.urls'

# Defines where Django looks for HTML templates and how it processes them
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # I can add custom template folders here later if needed
        'APP_DIRS': True,  # Tells Django to look for templates inside app folders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Points to my WSGI configuration file (used for deployment)
WSGI_APPLICATION = 'digi_haccp.wsgi.application'


# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------
# This connects my project to the PostgreSQL database using environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # I’m using PostgreSQL as my database
        'NAME': os.getenv('DB_NAME'),               # Database name (from .env file)
        'USER': os.getenv('DB_USER'),               # Database username
        'PASSWORD': os.getenv('DB_PASSWORD'),       # Database password
        'HOST': os.getenv('DB_HOST'),               # Database host address
        'PORT': os.getenv('DB_PORT'),               # Port used by PostgreSQL
    }
}

# For extra security, I’m overriding the secret key and debug mode using .env values
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'


# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
# Django’s built-in validators help enforce strong password rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
# Handles language and time settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -----------------------------
# STATIC FILES
# -----------------------------
# Tells Django where to look for static assets like CSS and images
STATIC_URL = 'static/'


# -----------------------------
# DEFAULT SETTINGS
# -----------------------------
# Sets default primary key type for all models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Tells Django to use my custom User model from the accounts app
AUTH_USER_MODEL = 'accounts.User'
