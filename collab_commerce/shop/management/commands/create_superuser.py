"""
Django management command to create a superuser from environment variables.
Usage: python manage.py create_superuser
Or set environment variables: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser from environment variables or interactively'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_USERNAME')
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_EMAIL')
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
            default=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Non-interactive mode (requires all arguments or env vars)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        noinput = options['noinput']

        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('A superuser already exists. Use Django admin to create more.')
            )
            return

        # Interactive mode if not all provided
        if not noinput:
            if not username:
                username = input('Username: ')
            if not email:
                email = input('Email address: ')
            if not password:
                password = getpass.getpass('Password: ')
                password_again = getpass.getpass('Password (again): ')
                if password != password_again:
                    self.stdout.write(self.style.ERROR('Passwords do not match.'))
                    return
        else:
            # Non-interactive mode - must have all values
            if not username or not email or not password:
                self.stdout.write(
                    self.style.ERROR(
                        'In non-interactive mode, you must provide --username, --email, and --password '
                        'or set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD'
                    )
                )
                return

        # Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )

