import os
import json
import google.genai as genai
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max
from apps.employees.models import Employee, Department
from apps.attendance.models import AttendanceRecord
from apps.leaves.models import LeaveRequest
from apps.payroll.models import PayrollRun, Payslip
from datetime import datetime, timedelta

class AIService:
    """AI service for HR queries using Google Gemini"""

    def __init__(self):
        # Configure Gemini AI with new google.genai package
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)

    def process_query(self, query, user):
        """Process a natural language query and return relevant HR data"""

        # Check user permissions and role
        user_permissions = self._get_user_permissions(user)

        # Create context about available data based on user permissions
        context = self._get_database_context(user_permissions)

        # Create the prompt for the AI
        prompt = f"""
        You are an AI HR assistant for a company. The user has the following role: {user.role}
        
        User Permissions: {', '.join(user_permissions)}
        
        You have access to the following data:

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
        - project_summary: Get project management information
        - leave_analytics: Get detailed leave analytics
        - performance_metrics: Get employee performance data
        - general_info: For general questions

        Response format:
        If you need data: {{"query_type": "type", "parameters": {{"key": "value"}}}}
        If direct response: {{"response": "your answer here"}}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            result = self._parse_ai_response(response.text)

            if 'query_type' in result:
                # Execute database query with user permissions
                data = self._execute_query(result['query_type'], result.get('parameters', {}), user)
                return self._format_response(data, result['query_type'], user)
            else:
                return result.get('response', 'I apologize, but I could not process your query.')

        except Exception as e:
            error_msg = str(e).lower()
            if 'quota' in error_msg or '429' in error_msg:
                # Fallback to direct database queries when API quota is exceeded
                return self._fallback_query(query)
            return f"I encountered an error processing your query: {str(e)}"

    def _get_user_permissions(self, user):
        """Get user permissions based on their role"""
        permissions = []

        if user.role == 'ADMIN_HR':
            permissions.extend([
                'view_all_employees', 'view_all_departments', 'view_attendance_data',
                'view_leave_data', 'view_payroll_data', 'view_project_data',
                'view_analytics'
            ])
        elif user.role == 'MANAGER':
            permissions.extend([
                'view_team_employees', 'view_department_stats', 'view_team_attendance',
                'view_team_leaves', 'view_team_projects', 'view_basic_payroll',
                'view_team_performance'
            ])
        elif user.role == 'EMPLOYEE':
            permissions.extend([
                'view_own_profile', 'view_own_attendance', 'view_own_leaves',
                'view_basic_payroll', 'view_public_projects'
            ])

        return permissions

    def _get_database_context(self, permissions=None):
        """Get context about available database data based on permissions"""
        if permissions is None:
            permissions = []

        context_parts = []

        if 'view_all_employees' in permissions or 'view_team_employees' in permissions:
            context_parts.append(f"- Total Employees: {Employee.objects.count()}")

        if 'view_all_departments' in permissions:
            context_parts.append(f"- Total Departments: {Department.objects.count()}")
            context_parts.append(f"- Departments: {', '.join(Department.objects.values_list('name', flat=True))}")

        if 'view_leave_data' in permissions or 'view_team_leaves' in permissions:
            context_parts.append(f"- Active Leave Requests: {LeaveRequest.objects.filter(status='PENDING').count()}")

        if 'view_attendance_data' in permissions or 'view_team_attendance' in permissions:
            context_parts.append(f"- Recent Attendance Records: {AttendanceRecord.objects.filter(date__gte=datetime.now().date() - timedelta(days=30)).count()}")

        if 'view_payroll_data' in permissions or 'view_basic_payroll' in permissions:
            context_parts.append(f"- Payroll Runs: {PayrollRun.objects.count()}")

        if 'view_project_data' in permissions or 'view_team_projects' in permissions or 'view_public_projects' in permissions:
            from apps.projects.models import Project, Task
            context_parts.append(f"- Total Projects: {Project.objects.count()}")
            context_parts.append(f"- Active Projects: {Project.objects.filter(status='IN_PROGRESS').count()}")

        return "\n".join(context_parts) if context_parts else "Limited access to HR data based on your role."

    def _parse_ai_response(self, response_text):
        """Parse the AI response to extract structured data"""
        try:
            # Try to parse as JSON
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # If not JSON, treat as direct response
            return {"response": response_text.strip()}

    def _execute_query(self, query_type, parameters, user=None):
        """Execute database queries based on query type with user permission filtering"""
        permissions = self._get_user_permissions(user) if user else []

        if query_type == 'employee_count':
            if 'view_all_employees' in permissions:
                return {
                    'total_employees': Employee.objects.count(),
                    'active_employees': Employee.objects.filter(user__is_active=True).count()
                }
            elif 'view_team_employees' in permissions:
                # For managers, show only their department/team
                try:
                    manager_employee = Employee.objects.get(user=user)
                    team_count = Employee.objects.filter(
                        models.Q(department=manager_employee.department) |
                        models.Q(manager=manager_employee)
                    ).count()
                    return {
                        'total_employees': team_count,
                        'active_employees': Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee),
                            user__is_active=True
                        ).count()
                    }
                except Employee.DoesNotExist:
                    return {'total_employees': 0, 'active_employees': 0}
            else:
                return {'error': 'Insufficient permissions to view employee counts'}

        elif query_type == 'department_stats':
            if 'view_all_departments' in permissions:
                stats = Department.objects.annotate(
                    employee_count=Count('employee')
                ).values('name', 'employee_count')
                return list(stats)
            elif 'view_department_stats' in permissions:
                # Managers see only their department
                try:
                    manager_employee = Employee.objects.get(user=user)
                    stats = Department.objects.filter(
                        id=manager_employee.department.id
                    ).annotate(
                        employee_count=Count('employee')
                    ).values('name', 'employee_count')
                    return list(stats)
                except Employee.DoesNotExist:
                    return []
            else:
                return {'error': 'Insufficient permissions to view department statistics'}

        elif query_type == 'employee_details':
            name = parameters.get('name', '')
            if name:
                base_queryset = Employee.objects.filter(
                    models.Q(user__first_name__icontains=name) |
                    models.Q(user__last_name__icontains=name) |
                    models.Q(user__username__icontains=name)
                ).select_related('user', 'department')

                if 'view_all_employees' in permissions:
                    employees = base_queryset
                elif 'view_team_employees' in permissions:
                    # Managers can see employees in their department or team
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        employees = base_queryset.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        )
                    except Employee.DoesNotExist:
                        employees = Employee.objects.none()
                elif 'view_own_profile' in permissions:
                    # Employees can only see their own profile
                    employees = base_queryset.filter(user=user)
                else:
                    return {'error': 'Insufficient permissions to view employee details'}

                return [{
                    'name': f"{emp.user.first_name} {emp.user.last_name}",
                    'position': emp.position,
                    'department': emp.department.name,
                    'salary': str(emp.salary) if 'view_payroll_data' in permissions or 'view_basic_payroll' in permissions else 'Hidden',
                    'hire_date': emp.hire_date.isoformat()
                } for emp in employees]
            return []

        elif query_type == 'attendance_summary':
            if 'view_attendance_data' in permissions or 'view_team_attendance' in permissions:
                days = parameters.get('days', 30)
                cutoff_date = datetime.now().date() - timedelta(days=days)

                base_queryset = AttendanceRecord.objects.filter(date__gte=cutoff_date)

                if 'view_team_attendance' in permissions and 'view_attendance_data' not in permissions:
                    # Managers see only their team's attendance
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        team_members = Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        ).values_list('user', flat=True)
                        base_queryset = base_queryset.filter(employee__user__in=team_members)
                    except Employee.DoesNotExist:
                        base_queryset = AttendanceRecord.objects.none()

                # Enhanced attendance analytics
                summary = base_queryset.aggregate(
                    total_records=Count('id'),
                    present_days=Count('id', filter=models.Q(status='PRESENT')),
                    absent_days=Count('id', filter=models.Q(status='ABSENT')),
                    late_days=Count('id', filter=models.Q(status='LATE')),
                    half_days=Count('id', filter=models.Q(status='HALF_DAY'))
                )

                # Additional analytics
                summary.update({
                    'attendance_rate': round((summary['present_days'] + summary['half_days'] * 0.5) / summary['total_records'] * 100, 2) if summary['total_records'] > 0 else 0,
                    'avg_work_hours': base_queryset.filter(check_out__isnull=False).aggregate(
                        avg_hours=models.Avg(models.F('check_out') - models.F('check_in'))
                    )['avg_hours'],
                    'overtime_days': base_queryset.filter(
                        models.Q(check_out__isnull=False) &
                        models.F('check_out') - models.F('check_in') > timedelta(hours=9)
                    ).count(),
                    'weekly_patterns': list(base_queryset.annotate(
                        weekday=models.ExtractWeekDay('date')
                    ).values('weekday').annotate(
                        present_count=Count('id', filter=models.Q(status='PRESENT'))
                    ).order_by('weekday'))
                })
                return summary
            else:
                return {'error': 'Insufficient permissions to view attendance data'}

        elif query_type == 'leave_summary':
            if 'view_leave_data' in permissions or 'view_team_leaves' in permissions:
                base_queryset = LeaveRequest.objects.all()

                if 'view_team_leaves' in permissions and 'view_leave_data' not in permissions:
                    # Managers see only their team's leave requests
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        team_members = Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        ).values_list('user', flat=True)
                        base_queryset = base_queryset.filter(employee__user__in=team_members)
                    except Employee.DoesNotExist:
                        base_queryset = LeaveRequest.objects.none()

                summary = base_queryset.aggregate(
                    total_requests=Count('id'),
                    pending_requests=Count('id', filter=models.Q(status='PENDING')),
                    approved_requests=Count('id', filter=models.Q(status='APPROVED'))
                )
                return summary
            else:
                return {'error': 'Insufficient permissions to view leave data'}

        elif query_type == 'payroll_summary':
            if 'view_payroll_data' in permissions or 'view_basic_payroll' in permissions:
                current_year = datetime.now().year
                current_month = datetime.now().month

                base_queryset = Payslip.objects.all()

                if 'view_basic_payroll' in permissions and 'view_payroll_data' not in permissions:
                    # Employees see only their own payroll data
                    base_queryset = base_queryset.filter(employee__user=user)

                # Enhanced payroll analytics
                summary = base_queryset.aggregate(
                    total_payslips=Count('id'),
                    total_amount=Sum('net_salary'),
                    avg_salary=Avg('net_salary'),
                    min_salary=Min('net_salary'),
                    max_salary=Max('net_salary'),
                    total_deductions=Sum('total_deductions'),
                    total_allowances=Sum('total_allowances')
                )

                # Monthly trends for current year
                monthly_trends = list(base_queryset.filter(
                    pay_period_start__year=current_year
                ).annotate(
                    month=models.ExtractMonth('pay_period_start')
                ).values('month').annotate(
                    total_paid=Sum('net_salary'),
                    avg_paid=Avg('net_salary'),
                    payslip_count=Count('id')
                ).order_by('month'))

                # Current month summary
                current_month_summary = base_queryset.filter(
                    pay_period_start__year=current_year,
                    pay_period_start__month=current_month
                ).aggregate(
                    current_month_total=Sum('net_salary'),
                    current_month_count=Count('id')
                )

                summary.update({
                    'monthly_trends': monthly_trends,
                    'current_month': current_month_summary,
                    'salary_distribution': list(base_queryset.values('net_salary').annotate(
                        count=Count('id')
                    ).order_by('net_salary')[:10])  # Top 10 salary ranges
                })

                return summary
            else:
                return {'error': 'Insufficient permissions to view payroll data'}

        elif query_type == 'project_summary':
            from apps.projects.models import Project, ProjectMember, Task
            if 'view_project_data' in permissions or 'view_public_projects' in permissions:
                base_projects = Project.objects.all()
                base_tasks = Task.objects.all()

                if 'view_team_projects' in permissions and 'view_project_data' not in permissions:
                    # Managers see only projects they're involved in
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        team_members = Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        ).values_list('user', flat=True)
                        project_ids = ProjectMember.objects.filter(
                            employee__user__in=team_members
                        ).values_list('project', flat=True)
                        base_projects = base_projects.filter(id__in=project_ids)
                        base_tasks = base_tasks.filter(project__in=base_projects)
                    except Employee.DoesNotExist:
                        base_projects = Project.objects.none()
                        base_tasks = Task.objects.none()

                summary = {
                    'total_projects': base_projects.count(),
                    'active_projects': base_projects.filter(status='IN_PROGRESS').count(),
                    'completed_projects': base_projects.filter(status='COMPLETED').count(),
                    'on_hold_projects': base_projects.filter(status='ON_HOLD').count(),
                    'total_tasks': base_tasks.count(),
                    'completed_tasks': base_tasks.filter(status='COMPLETED').count(),
                    'in_progress_tasks': base_tasks.filter(status='IN_PROGRESS').count(),
                    'overdue_tasks': base_tasks.filter(due_date__lt=datetime.now().date(), status__in=['TODO', 'IN_PROGRESS']).count(),
                    'project_members': ProjectMember.objects.filter(project__in=base_projects).count()
                }
                return summary
            else:
                return {'error': 'Insufficient permissions to view project data'}

        elif query_type == 'leave_analytics':
            if 'view_analytics' in permissions or 'view_leave_data' in permissions:
                base_queryset = LeaveRequest.objects.all()

                if 'view_team_leaves' in permissions and 'view_leave_data' not in permissions and 'view_analytics' not in permissions:
                    # Managers see only their team's leave requests
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        team_members = Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        ).values_list('user', flat=True)
                        base_queryset = base_queryset.filter(employee__user__in=team_members)
                    except Employee.DoesNotExist:
                        base_queryset = LeaveRequest.objects.none()

                # Detailed leave analytics
                current_year = datetime.now().year
                analytics = {
                    'total_requests': base_queryset.count(),
                    'pending_requests': base_queryset.filter(status='PENDING').count(),
                    'approved_requests': base_queryset.filter(status='APPROVED').count(),
                    'rejected_requests': base_queryset.filter(status='REJECTED').count(),
                    'this_year_requests': base_queryset.filter(created_at__year=current_year).count(),
                    'this_month_requests': base_queryset.filter(created_at__year=current_year, created_at__month=datetime.now().month).count(),
                    'leave_types': list(base_queryset.values('leave_type__name').annotate(count=Count('id')).order_by('-count')[:5]),
                    'avg_approval_time': base_queryset.filter(status='APPROVED').exclude(approved_at=None).aggregate(
                        avg_time=models.Avg(models.F('approved_at') - models.F('created_at'))
                    )['avg_time']
                }
                return analytics
            else:
                return {'error': 'Insufficient permissions to view leave analytics'}

        elif query_type == 'performance_metrics':
            if 'view_analytics' in permissions or 'view_performance_data' in permissions:
                base_queryset = Employee.objects.all()

                if 'view_team_performance' in permissions and 'view_performance_data' not in permissions and 'view_analytics' not in permissions:
                    # Managers see only their team's performance
                    try:
                        manager_employee = Employee.objects.get(user=user)
                        base_queryset = Employee.objects.filter(
                            models.Q(department=manager_employee.department) |
                            models.Q(manager=manager_employee)
                        )
                    except Employee.DoesNotExist:
                        base_queryset = Employee.objects.none()

                # Enhanced performance metrics
                current_year = datetime.now().year
                metrics = {
                    'total_employees': base_queryset.count(),
                    'active_employees': base_queryset.filter(is_active=True).count(),
                    'employees_with_manager': base_queryset.exclude(manager=None).count(),
                    'department_distribution': list(base_queryset.values('department__name').annotate(count=Count('id')).order_by('-count')),
                    'position_distribution': list(base_queryset.values('position').annotate(count=Count('id')).order_by('-count')[:10]),
                    'recent_hires': base_queryset.filter(hire_date__gte=datetime.now().date() - timedelta(days=90)).count(),
                    'avg_salary': base_queryset.filter(salary__isnull=False).aggregate(avg_salary=models.Avg('salary'))['avg_salary'],
                    'salary_range': {
                        'min': base_queryset.filter(salary__isnull=False).aggregate(min_salary=models.Min('salary'))['min_salary'],
                        'max': base_queryset.filter(salary__isnull=False).aggregate(max_salary=models.Max('salary'))['max_salary']
                    },
                    'tenure_distribution': list(base_queryset.annotate(
                        tenure_months=models.ExtractMonth(models.functions.Now() - models.F('hire_date'))
                    ).values('tenure_months').annotate(count=Count('id')).order_by('tenure_months')[:12])
                }
                return metrics
            else:
                return {'error': 'Insufficient permissions to view performance metrics'}

        return {}

    def _format_response(self, data, query_type, user=None):
        """Format the query results into a natural language response"""
        if isinstance(data, dict) and 'error' in data:
            return f"Sorry, {data['error']}. Please contact your administrator if you need access to this information."

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
                salary_info = f" (Salary: {emp['salary']})" if emp['salary'] != 'Hidden' else ""
                response += f"- {emp['name']}: {emp['position']} in {emp['department']}{salary_info} (Hired: {emp['hire_date']})\n"
            return response

        elif query_type == 'attendance_summary':
            attendance_rate = data.get('attendance_rate', 0)
            avg_hours = data.get('avg_work_hours')
            overtime_days = data.get('overtime_days', 0)
            hours_str = f" with an average of {avg_hours} hours worked per day" if avg_hours else ""
            overtime_str = f" and {overtime_days} overtime days" if overtime_days > 0 else ""
            return f"In the last 30 days, there were {data['total_records']} attendance records, with {data['present_days']} present days, {data['absent_days']} absent days, {data.get('late_days', 0)} late days, and {data.get('half_days', 0)} half days. Overall attendance rate: {attendance_rate}%{hours_str}{overtime_str}."

        elif query_type == 'leave_summary':
            return f"There are currently {data['total_requests']} leave requests: {data['pending_requests']} pending and {data['approved_requests']} approved."

        elif query_type == 'payroll_summary':
            avg_salary = data.get('avg_salary')
            current_month_total = data.get('current_month', {}).get('current_month_total', 0)
            current_month_count = data.get('current_month', {}).get('current_month_count', 0)
            avg_str = f" with an average salary of ${avg_salary:.2f}" if avg_salary else ""
            current_month_str = f" This month: ${current_month_total:.2f} paid to {current_month_count} employees." if current_month_total else ""
            return f"We've processed {data['total_payslips']} payslips with a total amount of ${data['total_amount'] or 0:.2f}{avg_str}.{current_month_str}"

        elif query_type == 'project_summary':
            return f"Project Overview:\n- Total Projects: {data['total_projects']}\n- Active Projects: {data['active_projects']}\n- Completed Projects: {data['completed_projects']}\n- Total Tasks: {data['total_tasks']}\n- Completed Tasks: {data['completed_tasks']}\n- Overdue Tasks: {data['overdue_tasks']}"

        elif query_type == 'leave_analytics':
            leave_types_str = "\n".join([f"- {item['leave_type__name']}: {item['count']} requests" for item in data['leave_types']])
            avg_time = data.get('avg_approval_time')
            time_str = f"\n- Average Approval Time: {avg_time}" if avg_time else ""
            return f"Leave Analytics:\n- Total Requests: {data['total_requests']}\n- Pending: {data['pending_requests']}\n- Approved: {data['approved_requests']}\n- Rejected: {data['rejected_requests']}\n- This Year: {data['this_year_requests']}\n- This Month: {data['this_month_requests']}{time_str}\n\nPopular Leave Types:\n{leave_types_str}"

        elif query_type == 'performance_metrics':
            dept_str = "\n".join([f"- {dept['department__name']}: {dept['count']} employees" for dept in data['department_distribution']])
            pos_str = "\n".join([f"- {pos['position']}: {pos['count']} employees" for pos in data['position_distribution'][:5]])
            avg_salary = data.get('avg_salary')
            salary_range = data.get('salary_range', {})
            salary_info = ""
            if avg_salary:
                salary_info = f"\n\nSalary Information:\n- Average Salary: ${avg_salary:.2f}\n- Salary Range: ${salary_range.get('min', 'N/A')} - ${salary_range.get('max', 'N/A')}"
            return f"Performance Metrics:\n- Total Employees: {data['total_employees']}\n- Active Employees: {data['active_employees']}\n- Employees with Managers: {data['employees_with_manager']}\n- Recent Hires (90 days): {data['recent_hires']}\n\nDepartment Distribution:\n{dept_str}\n\nTop Positions:\n{pos_str}{salary_info}"

        return "I've retrieved the requested data, but I'm not sure how to format it yet."

    def _fallback_query(self, query, user=None):
        """Fallback method to handle queries directly when AI API is unavailable"""
        permissions = self._get_user_permissions(user) if user else []
        query_lower = query.lower()

        if 'how many employees' in query_lower or 'employee count' in query_lower:
            data = self._execute_query('employee_count', {}, user)
            return self._format_response(data, 'employee_count', user)

        elif 'department' in query_lower and ('stats' in query_lower or 'statistics' in query_lower):
            data = self._execute_query('department_stats', {}, user)
            return self._format_response(data, 'department_stats', user)

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
                data = self._execute_query('employee_details', {'name': name}, user)
                return self._format_response(data, 'employee_details', user)
            else:
                return "Please specify which employee's details you'd like to see."

        elif 'attendance' in query_lower:
            data = self._execute_query('attendance_summary', {}, user)
            return self._format_response(data, 'attendance_summary', user)

        elif 'leave' in query_lower:
            data = self._execute_query('leave_summary', {}, user)
            return self._format_response(data, 'leave_summary', user)

        elif 'payroll' in query_lower:
            data = self._execute_query('payroll_summary', {}, user)
            return self._format_response(data, 'payroll_summary', user)

        elif 'project' in query_lower or 'task' in query_lower:
            data = self._execute_query('project_summary', {}, user)
            return self._format_response(data, 'project_summary', user)

        elif 'leave analytics' in query_lower or 'leave stats' in query_lower:
            data = self._execute_query('leave_analytics', {}, user)
            return self._format_response(data, 'leave_analytics', user)

        elif 'performance' in query_lower or 'metrics' in query_lower:
            data = self._execute_query('performance_metrics', {}, user)
            return self._format_response(data, 'performance_metrics', user)

        else:
            available_features = []
            if 'view_all_employees' in permissions or 'view_team_employees' in permissions:
                available_features.append('employee counts')
            if 'view_all_departments' in permissions or 'view_department_stats' in permissions:
                available_features.append('department statistics')
            if 'view_all_employees' in permissions or 'view_team_employees' in permissions or 'view_own_profile' in permissions:
                available_features.append('employee details')
            if 'view_attendance_data' in permissions or 'view_team_attendance' in permissions:
                available_features.append('attendance')
            if 'view_leave_data' in permissions or 'view_team_leaves' in permissions:
                available_features.append('leave')
            if 'view_payroll_data' in permissions or 'view_basic_payroll' in permissions:
                available_features.append('payroll')
            if 'view_project_data' in permissions or 'view_public_projects' in permissions:
                available_features.append('projects')
            if 'view_analytics' in permissions:
                available_features.extend(['leave analytics', 'performance metrics'])

            if available_features:
                return f"I'm currently operating in limited mode due to API quota restrictions. Based on your role, I can help with: {', '.join(available_features)}. Please try one of these queries!"
            else:
                return "I'm currently operating in limited mode due to API quota restrictions and your current permissions don't allow access to HR data. Please contact your administrator."