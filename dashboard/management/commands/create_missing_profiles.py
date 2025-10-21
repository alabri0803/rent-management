from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for users who don\'t have one'

    def handle(self, *args, **options):
        users_without_profile = []
        created_count = 0
        
        for user in User.objects.all():
            try:
                # Try to access profile
                profile = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=user)
                users_without_profile.append(user.username)
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} UserProfile(s) for users: {", ".join(users_without_profile)}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('All users already have UserProfile')
            )
