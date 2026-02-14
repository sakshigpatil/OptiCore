"""
AI-powered chatbot service using Google Gemini
Provides intelligent responses with database query capabilities
"""
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from datetime import datetime, timedelta
import json


class HRChatbotAI:
    """AI-powered HR Chatbot with database access"""
    
    def __init__(self):
        """Initialize Gemini AI with function calling"""
        # Configure Gemini API
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
        
        # Define available tools (functions AI can call)
        self.tools = [
            {
                "name": "get_employee_statistics",
                "description": "Get employee statistics including total employees, active employees, and department breakdown",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department": {
                            "type": "string",
                            "description": "Optional department name to filter by"
                        }
                    }
                }
            },
            {
                "name": "get_leave_requests",
                "description": "Get leave request information including pending, approved, or rejected leaves",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["PENDING", "APPROVED", "REJECTED", "ALL"],
                            "description": "Status of leave requests to fetch"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return (default 5)"
                        }
                    }
                }
            },
            {
                "name": "get_attendance_data",
                "description": "Get attendance statistics for today or a specific date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format (default: today)"
                        }
                    }
                }
            },
            {
                "name": "get_department_info",
                "description": "Get information about departments including employee count",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "department_name": {
                            "type": "string",
                            "description": "Specific department name to get info about"
                        }
                    }
                }
            },
            {
                "name": "search_employees",
                "description": "Search for employees by name, department, or role",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, email, etc.)"
                        },
                        "department": {
                            "type": "string",
                            "description": "Filter by department"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ACTIVE", "INACTIVE", "ALL"],
                            "description": "Employee status"
                        }
                    }
                }
            }
        ]
        
        # Initialize model with function calling
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            tools=self.tools if api_key else None
        )
        
        # System instruction for HR context
        self.system_instruction = """You are an intelligent HR Assistant for an HRMS (Human Resource Management System). 

Your role is to:
- Help users with HR-related queries about employees, leaves, attendance, and departments
- Provide accurate statistics by calling available database functions
- Be professional, friendly, and helpful
- Use emojis sparingly for better UX (📊, 👥, 📅, ⏰)
- Format responses clearly with bullet points and sections when needed
- If you don't have access to specific data, guide users on where to find it

Available data sources:
- Employee information (name, department, role, status)
- Leave requests (pending, approved, rejected)
- Attendance records (daily attendance status)
- Department information (employee count, names)

Always call the appropriate function to get real-time data instead of making assumptions."""

    def get_employee_statistics(self, department=None):
        """Get employee statistics from database"""
        from apps.employees.models import Employee, Department
        
        try:
            # Base query
            if department:
                employees = Employee.objects.filter(department__name__icontains=department)
                total_employees = employees.count()
                active_employees = employees.filter(status='ACTIVE').count()
            else:
                total_employees = Employee.objects.count()
                active_employees = Employee.objects.filter(status='ACTIVE').count()
            
            # Department breakdown
            dept_stats = Department.objects.annotate(
                emp_count=Count('employee')
            ).values('name', 'emp_count').order_by('-emp_count')
            
            return {
                "total_employees": total_employees,
                "active_employees": active_employees,
                "inactive_employees": total_employees - active_employees,
                "departments": list(dept_stats)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_leave_requests(self, status="PENDING", limit=5):
        """Get leave requests from database"""
        from apps.leaves.models import LeaveRequest
        
        try:
            if status == "ALL":
                leaves = LeaveRequest.objects.all()
            else:
                leaves = LeaveRequest.objects.filter(status=status)
            
            leaves = leaves.select_related('employee__user', 'leave_type').order_by('-created_at')[:limit]
            
            leave_data = []
            for leave in leaves:
                leave_data.append({
                    "employee_name": leave.employee.user.get_full_name(),
                    "leave_type": leave.leave_type.name,
                    "start_date": str(leave.start_date),
                    "end_date": str(leave.end_date),
                    "days": leave.days_requested,
                    "status": leave.status,
                    "reason": leave.reason[:100] if leave.reason else ""
                })
            
            # Get counts by status
            pending_count = LeaveRequest.objects.filter(status='PENDING').count()
            approved_count = LeaveRequest.objects.filter(status='APPROVED').count()
            rejected_count = LeaveRequest.objects.filter(status='REJECTED').count()
            
            return {
                "leaves": leave_data,
                "total_count": len(leave_data),
                "pending_count": pending_count,
                "approved_count": approved_count,
                "rejected_count": rejected_count
            }
        except Exception as e:
            return {"error": str(e)}

    def get_attendance_data(self, date=None):
        """Get attendance statistics"""
        from apps.attendance.models import AttendanceRecord
        from apps.employees.models import Employee
        
        try:
            if date:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date()
            
            present_count = AttendanceRecord.objects.filter(
                date=target_date,
                status='PRESENT'
            ).count()
            
            absent_count = AttendanceRecord.objects.filter(
                date=target_date,
                status='ABSENT'
            ).count()
            
            late_count = AttendanceRecord.objects.filter(
                date=target_date,
                status='LATE'
            ).count()
            
            total_active = Employee.objects.filter(status='ACTIVE').count()
            attendance_rate = (present_count / total_active * 100) if total_active > 0 else 0
            
            return {
                "date": str(target_date),
                "present": present_count,
                "absent": absent_count,
                "late": late_count,
                "total_active_employees": total_active,
                "attendance_rate": round(attendance_rate, 2)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_department_info(self, department_name=None):
        """Get department information"""
        from apps.employees.models import Department
        
        try:
            if department_name:
                departments = Department.objects.filter(name__icontains=department_name)
            else:
                departments = Department.objects.all()
            
            dept_data = departments.annotate(
                emp_count=Count('employee')
            ).values('name', 'emp_count')
            
            return {
                "departments": list(dept_data),
                "total_departments": departments.count()
            }
        except Exception as e:
            return {"error": str(e)}

    def search_employees(self, query=None, department=None, status="ACTIVE"):
        """Search employees"""
        from apps.employees.models import Employee
        
        try:
            employees = Employee.objects.select_related('user', 'department')
            
            if status != "ALL":
                employees = employees.filter(status=status)
            
            if department:
                employees = employees.filter(department__name__icontains=department)
            
            if query:
                employees = employees.filter(
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(user__email__icontains=query) |
                    Q(employee_id__icontains=query)
                )
            
            emp_data = []
            for emp in employees[:10]:  # Limit to 10 results
                emp_data.append({
                    "name": emp.user.get_full_name(),
                    "email": emp.user.email,
                    "employee_id": emp.employee_id,
                    "department": emp.department.name if emp.department else "N/A",
                    "designation": emp.designation or "N/A",
                    "status": emp.status
                })
            
            return {
                "employees": emp_data,
                "total_found": employees.count()
            }
        except Exception as e:
            return {"error": str(e)}

    def call_function(self, function_name, arguments):
        """Execute a function call from AI"""
        function_map = {
            "get_employee_statistics": self.get_employee_statistics,
            "get_leave_requests": self.get_leave_requests,
            "get_attendance_data": self.get_attendance_data,
            "get_department_info": self.get_department_info,
            "search_employees": self.search_employees
        }
        
        if function_name in function_map:
            return function_map[function_name](**arguments)
        else:
            return {"error": f"Unknown function: {function_name}"}

    def process_message(self, user_message, user_name="User"):
        """Process user message and generate AI response"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        # If no API key, use fallback pattern matching
        if not api_key:
            return self._fallback_response(user_message)
        
        try:
            # Start chat with system instruction
            chat = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [self.system_instruction]
                    },
                    {
                        "role": "model",
                        "parts": [f"Understood! I'm ready to assist with HR queries. Hello {user_name}!"]
                    }
                ]
            )
            
            # Send user message
            response = chat.send_message(user_message)
            
            # Handle function calls
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        # Execute the function
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        # Call the function
                        function_result = self.call_function(function_name, function_args)
                        
                        # Send function result back to AI
                        response = chat.send_message(
                            genai.protos.Content(
                                parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={"result": function_result}
                                    )
                                )]
                            )
                        )
            
            # Return the final response
            return {
                "message": response.text,
                "metadata": {
                    "type": "ai_response",
                    "model": "gemini-1.5-flash"
                }
            }
        
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return {
                "message": f"I encountered an error processing your request. Please try rephrasing your question.",
                "metadata": {"type": "error", "error": str(e)}
            }

    def _fallback_response(self, message):
        """Fallback response when API key is not configured"""
        return {
            "message": """⚠️ **AI Mode Not Configured**

To enable intelligent AI responses, you need to:

1. Get a free Google Gemini API key from: https://makersuite.google.com/app/apikey
2. Add it to your settings:
   - Create/update `.env` file in backend folder
   - Add: `GEMINI_API_KEY=your_api_key_here`
3. Restart the Django server

For now, I can still help with:
• Employee statistics
• Leave requests  
• Attendance data
• Department information

Just ask using keywords like "show employees", "pending leaves", etc.""",
            "metadata": {"type": "config_required"}
        }


# Global instance
chatbot_ai = HRChatbotAI()
