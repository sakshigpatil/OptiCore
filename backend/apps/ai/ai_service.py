import os
import json
import google.generativeai as genai
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg
from apps.employees.models import Employee, Department
from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest
from apps.payroll.models import PayrollRun, Payslip
from datetime import datetime, timedelta

class AIService:
    """AI service for HR queries using Google Gemini"""

    def __init__(self):
        # Configure Gemini AI
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        
        # Use a stable model
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def process_query(self, query, user):
        """Process a natural language query and return relevant HR data"""

        # Create context about available data
        context = self._get_database_context()

        # Create the prompt for the AI
        prompt = f"""
        You are an AI HR assistant for a company. You have access to the following data:

        {context}

        User Query: {query}

        Please analyze the query and provide a helpful response. If the query asks for specific data, retrieve it from the available information.
        If you need to query the database, respond with a JSON object containing the query type and parameters.
        Otherwise, provide a natural language response.

        Available query types:
        - employee_count: Get total number of employees
        - department_stats: Get statistics by department
        - employee_details: Get details for a specific employee
        - attendance_summary: Get attendance information
        - leave_summary: Get leave information
        - payroll_summary: Get payroll information
        - general_info: For general questions

        Response format:
        If you need data: {{"query_type": "type", "parameters": {{"key": "value"}}}}
        If direct response: {{"response": "your answer here"}}
        """

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_ai_response(response.text)

            if 'query_type' in result:
                # Execute database query
                data = self._execute_query(result['query_type'], result.get('parameters', {}))
                return self._format_response(data, result['query_type'])
            else:
                return result.get('response', 'I apologize, but I could not process your query.')

        except Exception as e:
            error_msg = str(e).lower()
            if 'quota' in error_msg or '429' in error_msg:
                # Fallback to direct database queries when API quota is exceeded
                return self._fallback_query(query)
            return f"I encountered an error processing your query: {str(e)}"

    def _get_database_context(self):
        """Get context about available database data"""
        context = f"""
        Current Database Summary:
        - Total Employees: {Employee.objects.count()}
        - Total Departments: {Department.objects.count()}
        - Departments: {', '.join(Department.objects.values_list('name', flat=True))}
        - Active Leave Requests: {LeaveRequest.objects.filter(status='PENDING').count()}
        - Recent Attendance Records: {AttendanceRecord.objects.filter(date__gte=datetime.now().date() - timedelta(days=30)).count()}
        - Payroll Runs: {PayrollRun.objects.count()}
        """

        return context

    def _parse_ai_response(self, response_text):
        """Parse the AI response to extract structured data"""
        try:
            # Try to parse as JSON
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # If not JSON, treat as direct response
            return {"response": response_text.strip()}

    def _execute_query(self, query_type, parameters):
        """Execute database queries based on query type"""
        if query_type == 'employee_count':
            return {
                'total_employees': Employee.objects.count(),
                'active_employees': Employee.objects.filter(user__is_active=True).count()
            }

        elif query_type == 'department_stats':
            stats = Department.objects.annotate(
                employee_count=Count('employee')
            ).values('name', 'employee_count')
            return list(stats)

        elif query_type == 'employee_details':
            name = parameters.get('name', '')
            if name:
                employees = Employee.objects.filter(
                    models.Q(user__first_name__icontains=name) |
                    models.Q(user__last_name__icontains=name) |
                    models.Q(user__username__icontains=name)
                ).select_related('user', 'department')
                return [{
                    'name': f"{emp.user.first_name} {emp.user.last_name}",
                    'position': emp.position,
                    'department': emp.department.name,
                    'salary': str(emp.salary),
                    'hire_date': emp.hire_date.isoformat()
                } for emp in employees]
            return []

        elif query_type == 'attendance_summary':
            days = parameters.get('days', 30)
            cutoff_date = datetime.now().date() - timedelta(days=days)
            summary = AttendanceRecord.objects.filter(
                date__gte=cutoff_date
            ).aggregate(
                total_records=Count('id'),
                present_days=Count('id', filter=models.Q(status='PRESENT')),
                absent_days=Count('id', filter=models.Q(status='ABSENT'))
            )
            return summary

        elif query_type == 'leave_summary':
            summary = LeaveRequest.objects.aggregate(
                total_requests=Count('id'),
                pending_requests=Count('id', filter=models.Q(status='PENDING')),
                approved_requests=Count('id', filter=models.Q(status='APPROVED'))
            )
            return summary

        elif query_type == 'payroll_summary':
            summary = Payslip.objects.aggregate(
                total_payslips=Count('id'),
                total_amount=Sum('net_salary')
            )
            return summary

        return {}

    def _format_response(self, data, query_type):
        """Format the query results into a natural language response"""
        if query_type == 'employee_count':
            return f"We currently have {data['total_employees']} total employees, with {data['active_employees']} active employees."

        elif query_type == 'department_stats':
            response = "Here's the employee distribution by department:\n"
            for dept in data:
                response += f"- {dept['name']}: {dept['employee_count']} employees\n"
            return response

        elif query_type == 'employee_details':
            if not data:
                return "I couldn't find any employees matching that name."
            response = "Here are the employee details:\n"
            for emp in data:
                response += f"- {emp['name']}: {emp['position']} in {emp['department']} (Hired: {emp['hire_date']})\n"
            return response

        elif query_type == 'attendance_summary':
            return f"In the last 30 days, there were {data['total_records']} attendance records, with {data['present_days']} present days and {data['absent_days']} absent days."

        elif query_type == 'leave_summary':
            return f"There are currently {data['total_requests']} leave requests: {data['pending_requests']} pending and {data['approved_requests']} approved."

        elif query_type == 'payroll_summary':
            return f"We've processed {data['total_payslips']} payslips with a total amount of ${data['total_amount'] or 0}."

        return "I've retrieved the requested data, but I'm not sure how to format it yet."

    def _fallback_query(self, query):
        """Fallback method to handle queries directly when AI API is unavailable"""
        query_lower = query.lower()

        if 'how many employees' in query_lower or 'employee count' in query_lower:
            data = self._execute_query('employee_count', {})
            return self._format_response(data, 'employee_count')

        elif 'department' in query_lower and ('stats' in query_lower or 'statistics' in query_lower):
            data = self._execute_query('department_stats', {})
            return self._format_response(data, 'department_stats')

        elif 'employee' in query_lower and ('details' in query_lower or 'info' in query_lower):
            # Try to extract name from query
            name = None
            if 'priya' in query_lower:
                name = 'priya'
            elif 'rajesh' in query_lower:
                name = 'rajesh'
            elif 'arjun' in query_lower:
                name = 'arjun'
            elif 'anita' in query_lower:
                name = 'anita'
            elif 'vikram' in query_lower:
                name = 'vikram'

            if name:
                data = self._execute_query('employee_details', {'name': name})
                return self._format_response(data, 'employee_details')
            else:
                return "Please specify which employee's details you'd like to see."

        elif 'attendance' in query_lower:
            data = self._execute_query('attendance_summary', {})
            return self._format_response(data, 'attendance_summary')

        elif 'leave' in query_lower:
            data = self._execute_query('leave_summary', {})
            return self._format_response(data, 'leave_summary')

        elif 'payroll' in query_lower:
            data = self._execute_query('payroll_summary', {})
            return self._format_response(data, 'payroll_summary')

        else:
            return "I'm currently operating in limited mode due to API quota restrictions. I can help with employee counts, department statistics, employee details (Priya, Rajesh, Arjun, Anita, Vikram), attendance, leave, and payroll summaries. Please try one of these queries!"