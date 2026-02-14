#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.leaves.models import LeaveRequest

User = get_user_model()

def test_approve_leave():
    print("Testing Leave Approval API...")
    
    # Login to get token
    login_data = {
        'email': 'admin@hrms.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/v1/auth/login/', 
                               json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get pending leave requests
            leave_response = requests.get(
                'http://localhost:8000/api/v1/leaves/leave-requests/',
                headers=headers
            )
            
            if leave_response.status_code == 200:
                leave_data = leave_response.json()
                print(f"Leave data type: {type(leave_data)}")
                
                # Handle both list format and paginated format
                if isinstance(leave_data, list):
                    requests_list = leave_data
                elif isinstance(leave_data, dict) and 'results' in leave_data:
                    requests_list = leave_data['results']
                else:
                    requests_list = leave_data if isinstance(leave_data, list) else []
                
                pending_requests = [req for req in requests_list if req.get('status') == 'PENDING']
                
                print(f"Found {len(pending_requests)} pending leave requests")
                
                if pending_requests:
                    # Test approving the first pending request
                    request_id = pending_requests[0]['id']
                    print(f"Approving request ID: {request_id}")
                    
                    approve_response = requests.post(
                        f'http://localhost:8000/api/v1/leaves/leave-requests/{request_id}/approve/',
                        headers=headers
                    )
                    
                    if approve_response.status_code == 200:
                        print("✅ Leave request approved successfully!")
                        print(approve_response.json().get('message'))
                    else:
                        print(f"❌ Approve failed: {approve_response.status_code}")
                        print(approve_response.text)
                else:
                    print("No pending requests to test")
                    
        else:
            print(f"❌ Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_approve_leave()