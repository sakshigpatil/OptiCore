#!/usr/bin/env python
"""
Simple script to create test users for HRMS login
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_users():
    print("Creating test users...")
    
    # Create users with proper passwords
    users_data = [
        {
            'username': 'priya.sharma', 
            'email': 'priya.sharma@hrms.com',
            'first_name': 'Priya', 
            'last_name': 'Sharma', 
            'role': 'ADMIN_HR',
            'is_staff': True, 
            'is_superuser': True,
            'password': 'password123'
        },
        {
            'username': 'rajesh.kumar', 
            'email': 'rajesh.kumar@hrms.com',
            'first_name': 'Rajesh', 
            'last_name': 'Kumar', 
            'role': 'MANAGER',
            'password': 'password123'
        },
        {
            'username': 'arjun.patel', 
            'email': 'arjun.patel@hrms.com',
            'first_name': 'Arjun', 
            'last_name': 'Patel', 
            'role': 'MANAGER',
            'password': 'password123'
        },
        {
            'username': 'anita.singh', 
            'email': 'anita.singh@hrms.com',
            'first_name': 'Anita', 
            'last_name': 'Singh', 
            'role': 'EMPLOYEE',
            'password': 'password123'
        },
        {
            'username': 'vikram.mehta', 
            'email': 'vikram.mehta@hrms.com',
            'first_name': 'Vikram', 
            'last_name': 'Mehta', 
            'role': 'EMPLOYEE',
            'password': 'password123'
        },
    ]
    
    for user_data in users_data:
        password = user_data.pop('password')
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(password)
            user.is_approved = True
            user.approval_status = 'APPROVED'
            user.save()
            print(f"✅ Created user: {user.username} (password: {password})")
        else:
            # Update password and approval for existing user
            user.set_password(password)
            user.is_approved = True
            user.approval_status = 'APPROVED'
            user.save()
            print(f"🔄 Updated password for existing user: {user.username} (password: {password})")
    
    print("\n🎉 Test users created successfully!")
    print("\n📋 Login credentials:")
    print("===================")
    for user_data in users_data:
        print(f"Email: {user_data['email']} | Password: password123")

if __name__ == "__main__":
    create_test_users()