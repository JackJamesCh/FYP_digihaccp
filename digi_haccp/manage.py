#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # This line tells Django which settings file to use for this project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digi_haccp.settings')

    try:
        # Imports Django’s built-in command-line tools
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If Django isn’t installed or the virtual environment isn’t active,
        # this error message helps identify the problem
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # This runs the command-line instructions (like runserver, makemigrations, etc.)
    execute_from_command_line(sys.argv)


# This makes sure the main() function runs when this file is executed directly
if __name__ == '__main__':
    main()
