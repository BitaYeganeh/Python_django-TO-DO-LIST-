from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tasks.models import Task

DEMO_TASKS = [
    'Welcome to the Demo 👋',
    'This app uses Django',
    'Sign up to create your own tasks!',
    'Check daily Emails',
    'Check Calendar for daily meetings',
    'Buy groceries',
    'Finish Django project',
]


class Command(BaseCommand):
    help = 'Create the read-only demo_user and its demo tasks (safe to run repeatedly).'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username='demo_user')
        if created:
            user.set_unusable_password()  # nobody can log in as the demo user
            user.save()
        for title in DEMO_TASKS:
            Task.objects.get_or_create(user=user, title=title)
        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
