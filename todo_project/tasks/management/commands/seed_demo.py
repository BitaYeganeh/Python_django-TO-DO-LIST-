from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tasks.models import Task

# (title, note, done) — a few are done so the demo shows ticks and progress
DEMO_TASKS = [
    ('Welcome to the Demo 👋', 'Sign up to create your own list', False),
    ('Buy groceries', 'Milk, bread, coffee', False),
    ('Check Calendar for daily meetings', '', False),
    ('Finish Django project', '', False),
    ('This app uses Django', '', True),
    ('Check daily Emails', '', True),
]


class Command(BaseCommand):
    help = 'Create the read-only demo_user and its demo tasks (safe to run repeatedly).'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username='demo_user')
        if created:
            user.set_unusable_password()  # nobody can log in as the demo user
            user.save()
        for title, note, done in DEMO_TASKS:
            Task.objects.get_or_create(
                user=user,
                title=title,
                defaults={'description': note, 'completed': done},
            )
        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
