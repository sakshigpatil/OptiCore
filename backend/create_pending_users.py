#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_pending_users():
    print("Creating sample pending users...")
    
    # Sample pending user data
    pending_users_data = [
        {
            'username': 'john.doe',
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'EMPLOYEE',
            'phone': '+1-555-0123'
        },
        {
            'username': 'jane.smith',
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'MANAGER',
            'phone': '+1-555-0124'
        },
        {
            'username': 'mike.johnson',
            'email': 'mike.johnson@example.com',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'role': 'EMPLOYEE',
            'phone': '+1-555-0125'
        }
    ]
    
    created_users = []
    
    for user_data in pending_users_data:
        # Check if user already exists
        if User.objects.filter(email=user_data['email']).exists():
            print(f"User with email {user_data['email']} already exists")
            continue
            
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password='temppassword123',
            role=user_data['role'],
            phone=user_data.get('phone'),
            is_approved=False,
            approval_status='PENDING'
        )
        created_users.append(user)
        print(f"Created pending user: {user.get_full_name()} ({user.email})")
    
    print(f"\nTotal pending users: {User.objects.filter(approval_status='PENDING').count()}")
    
    # Show all pending users
    pending_users = User.objects.filter(approval_status='PENDING')
    for user in pending_users:
        print(f"- {user.get_full_name()} ({user.email}) - {user.role} - {user.approval_status}")

if __name__ == "__main__":
    create_pending_users()