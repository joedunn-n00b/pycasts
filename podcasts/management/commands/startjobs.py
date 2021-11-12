# you’re going to be adding jobs to this file with django-apscheduler,
# which is why you named the file startjobs.py.
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("It works!")