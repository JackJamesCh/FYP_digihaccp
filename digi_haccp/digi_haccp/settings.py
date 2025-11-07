"""
Django settings for digi_haccp project.
Generated automatically when I created the project using 'django-admin startproject'.
This file controls how my whole Django app runs — including database setup,
installed apps, templates, and security configurations.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# I used dotenv to keep sensitive data (database credentials and secret keys) outside of my code
load_dotenv()

# This points to the main directory of my Django project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY & DEBUG SETTINGS
# The secret key is used for encryption
SECRET_KEY = 'django-insecure-9u$s3b2(%d#x%*sgu=!*@x*5u-*%4@tb69e17=#vrrl&vsoti_'

# DEBUG helps me see detailed errors during development
# I only use this in development — it must be False in production
DEBUG = True

# ALLOWED_HOSTS defines which domains or IPs can access my app
ALLOWED_HOSTS = []

# INSTALLED APPS
INSTALLED_APPS = [
    # My custom app for user accounts, logins, and delis
    'accounts',
    # Default Django apps that provide essential features
    'django.contrib.admin',         # Admin dashboard
    'django.contrib.auth',          # Authentication system
    'django.contrib.contenttypes',  # Model content handling
    'django.contrib.sessions',      # Session management
    'django.contrib.messages',      # Displaying temporary messages
    'django.contrib.staticfiles',   # Managing static files
    'widget_tweaks',                # I added this to easily style Django forms
]

# MIDDLEWARE
# Middleware handles security, sessions, and requests between the browser and the server
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Helps protect my forms from CSRF attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles login sessions
    'django.contrib.messages.middleware.MessageMiddleware',      # Displays feedback messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    # Adds security headers
]

# URLS & TEMPLATES
# ROOT_URLCONF tells Django where my main URL routes are stored
ROOT_URLCONF = 'digi_haccp.urls'

# TEMPLATES tells Django where to find my HTML files and how to render them
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # I could add a global template folder later if needed
        'APP_DIRS': True,  # Automatically loads templates from my app folders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # Lets me access request data in templates
                'django.contrib.auth.context_processors.auth', # Makes user data available in templates
                'django.contrib.messages.context_processors.messages', # Passes messages to the frontend
            ],
        },
    },
]

# WSGI file is used when deploying my Django app to a live server
WSGI_APPLICATION = 'digi_haccp.wsgi.application'

# DATABASE SETTINGS
# I connected my project to PostgreSQL using environment variables for better security
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # I’m using PostgreSQL
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# I override the SECRET_KEY and DEBUG settings from my .env file for safety
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

# PASSWORD VALIDATION
# These validators help make sure passwords are strong and secure
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
# These settings define language, timezone, and localization options
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES
# This defines where Django looks for static assets like CSS, JS, and images
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # This makes Django look inside the static folder I created
]

# DEFAULT CONFIGURATION
# This is the default primary key type for all my database models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# This tells Django to use my custom User model instead of the default one
AUTH_USER_MODEL = 'accounts.User'