from django.core.management.base import BaseCommand

from apps.users.models import AppUser


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-e', '--email',
                            dest='email',
                            type=str,
                            help='email')

        parser.add_argument('-p', '--password',
                            dest='password',
                            type=str,
                            help='password')

    def handle(self, *args, **options):
        admin_exists = AppUser.objects.filter(is_active=True, is_superuser=True).exists()
        if not admin_exists:
            AppUser.objects.create_superuser(email=options['email'], password=options['password'])
