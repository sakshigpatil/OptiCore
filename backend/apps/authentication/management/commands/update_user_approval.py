from django.core.management.base import BaseCommand
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Update existing users with approval status'

    def handle(self, *args, **options):
        # Update HR and Manager users to be approved
        hr_users = User.objects.filter(role__in=['ADMIN_HR', 'MANAGER'])
        for user in hr_users:
            user.is_approved = True
            user.approval_status = 'APPROVED'
            user.save()
            self.stdout.write(f'Updated user {user.email} to approved status')

        # Show current status of all users
        users = User.objects.all()
        self.stdout.write('\nCurrent user statuses:')
        for user in users:
            self.stdout.write(f'{user.email}: {user.role} - {user.approval_status} - Can login: {user.can_login}')