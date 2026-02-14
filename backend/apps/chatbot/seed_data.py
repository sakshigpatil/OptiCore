"""
Seed data for chatbot knowledge base
"""

CHATBOT_KNOWLEDGE = [
    {
        'category': 'GENERAL',
        'question': 'What is this chatbot?',
        'answer': 'I am your HR Assistant, here to help you with employee management, leave requests, attendance tracking, payroll information, and general HR queries. Feel free to ask me anything!',
        'keywords': ['chatbot', 'assistant', 'help', 'what are you', 'who are you'],
        'priority': 100
    },
    {
        'category': 'LEAVE',
        'question': 'How do I approve a leave request?',
        'answer': 'To approve a leave request:\n1. Go to the Leaves tab in the HR dashboard\n2. Find the pending leave request\n3. Click on "Review" or the employee name\n4. Click "Approve" and optionally add comments\n\nYou can also ask me to show pending leave requests directly!',
        'keywords': ['approve leave', 'leave approval', 'accept leave', 'approve vacation'],
        'priority': 90
    },
    {
        'category': 'LEAVE',
        'question': 'What are the different types of leaves?',
        'answer': 'Common leave types in our system include:\n• Sick Leave\n• Casual Leave\n• Paid Leave\n• Annual Leave\n• Maternity/Paternity Leave\n• Unpaid Leave\n\nEach employee has specific leave balances that can be viewed in their profile.',
        'keywords': ['leave types', 'vacation types', 'time off types', 'leave categories'],
        'priority': 80
    },
    {
        'category': 'ATTENDANCE',
        'question': 'How is attendance tracked?',
        'answer': 'Attendance is tracked daily with statuses:\n• Present - Employee checked in on time\n• Late - Employee checked in late\n• Absent - Employee did not check in\n• On Leave - Employee is on approved leave\n• Half Day - Employee worked partial hours\n\nYou can view attendance reports, mark attendance, and generate attendance summaries from the Attendance tab.',
        'keywords': ['attendance', 'track attendance', 'attendance system', 'check in'],
        'priority': 85
    },
    {
        'category': 'EMPLOYEE',
        'question': 'How do I add a new employee?',
        'answer': 'To add a new employee:\n1. Go to the Employees tab\n2. Click "Add Employee" button\n3. Fill in employee details (name, email, department, position, etc.)\n4. Set employment details (joining date, salary, etc.)\n5. Click "Save"\n\nThe new employee will receive login credentials to access the employee portal.',
        'keywords': ['add employee', 'new employee', 'hire employee', 'onboard employee'],
        'priority': 95
    },
    {
        'category': 'EMPLOYEE',
        'question': 'How do I update employee information?',
        'answer': 'To update employee information:\n1. Go to the Employees tab\n2. Search for or click on the employee\n3. Click "Edit" or "Update Profile"\n4. Modify the necessary fields\n5. Click "Save Changes"\n\nYou can update personal details, job information, department assignments, and contact information.',
        'keywords': ['update employee', 'edit employee', 'modify employee', 'change employee details'],
        'priority': 85
    },
    {
        'category': 'PAYROLL',
        'question': 'How is payroll calculated?',
        'answer': 'Payroll calculation includes:\n• Base Salary\n• Allowances (HRA, DA, Medical, etc.)\n• Deductions (Tax, PF, Professional Tax)\n• Bonuses and Incentives\n• Overtime (if applicable)\n\nNet Salary = Gross Salary - Total Deductions\n\nPayroll is typically processed monthly and employees can view their payslips in the employee portal.',
        'keywords': ['payroll', 'salary calculation', 'pay calculation', 'salary process'],
        'priority': 90
    },
    {
        'category': 'POLICY',
        'question': 'What is the leave policy?',
        'answer': 'Standard Leave Policy:\n• Annual Leave: 15-20 days per year\n• Sick Leave: 10-12 days per year\n• Casual Leave: 7-10 days per year\n• Leave must be applied in advance (except emergencies)\n• Manager approval required\n• Unused leaves may be carried forward (company policy)\n\nContact HR for specific policy details.',
        'keywords': ['leave policy', 'vacation policy', 'time off policy', 'leave rules'],
        'priority': 75
    },
    {
        'category': 'POLICY',
        'question': 'What is the attendance policy?',
        'answer': 'Attendance Policy:\n• Employees must mark attendance daily\n• Working hours: 9 AM - 6 PM (or as per department)\n• Grace period: 15 minutes\n• Late arrival beyond grace period is marked as "Late"\n• Multiple late arrivals may affect performance review\n• Notify manager for planned absences\n• Unplanned absences require justification',
        'keywords': ['attendance policy', 'work hours', 'attendance rules', 'late policy'],
        'priority': 70
    },
    {
        'category': 'GENERAL',
        'question': 'How do I generate reports?',
        'answer': 'Reports available:\n• Employee Reports - List of all employees, department-wise\n• Attendance Reports - Daily, weekly, monthly attendance\n• Leave Reports - Leave balance, leave history\n• Payroll Reports - Salary statements, deduction reports\n\nMost reports can be exported to Excel or PDF from their respective sections.',
        'keywords': ['reports', 'generate report', 'export data', 'download report'],
        'priority': 80
    },
    {
        'category': 'BENEFITS',
        'question': 'What employee benefits are tracked?',
        'answer': 'Employee benefits typically include:\n• Health Insurance\n• Provident Fund (PF)\n• Gratuity\n• Medical Reimbursements\n• Travel Allowances\n• Performance Bonuses\n\nBenefits are configured per employee or department and reflected in payroll.',
        'keywords': ['benefits', 'employee benefits', 'insurance', 'perks'],
        'priority': 65
    },
    {
        'category': 'RECRUITMENT',
        'question': 'How is recruitment managed?',
        'answer': 'Recruitment workflow:\n1. Job posting and requirement definition\n2. Candidate applications review\n3. Screening and shortlisting\n4. Interview scheduling\n5. Selection and offer letter\n6. Onboarding process\n\nPending employee approvals can be managed from the Employee Approvals section.',
        'keywords': ['recruitment', 'hiring', 'onboarding', 'job posting'],
        'priority': 70
    },
]
