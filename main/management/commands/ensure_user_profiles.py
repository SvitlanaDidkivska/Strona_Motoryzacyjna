from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import UserProfile

class Command(BaseCommand):
    help = 'Ensures all users have associated UserProfile instances'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        created_count = 0

        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} user profiles'))
