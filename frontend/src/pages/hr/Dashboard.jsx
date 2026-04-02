import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';
import {
  UsersIcon,
  UserPlusIcon,
  ClockIcon,
  ExclamationCircleIcon,
  CurrencyDollarIcon,
  PlusIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  CalendarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import toast from 'react-hot-toast';

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

// Department color mapping
const DEPARTMENT_COLORS = {
  'HR': '#8B5CF6',           // Purple
  'Human Resources': '#8B5CF6', // Purple
  'Engineering': '#4F46E5',  // Blue
  'IT': '#4F46E5',          // Blue
  'Sales': '#F59E0B',       // Yellow
  'Marketing': '#F59E0B',   // Yellow
  'IT Support': '#10B981',  // Green
  'Support': '#10B981',     // Green
  'Operations': '#06B6D4',  // Cyan
  'Finance': '#EF4444',     // Red
  'Administration': '#64748B' // Gray
};

const getDepartmentColor = (departmentName) => {
  return DEPARTMENT_COLORS[departmentName] || COLORS[Math.floor(Math.random() * COLORS.length)];
};

function MetricCard({ title, value, subtitle, icon: Icon, colorClass, trend, trendValue }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer group">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <Icon className={`h-5 w-5 ${colorClass}`} />
            <p className="text-sm font-medium text-gray-600">{title}</p>
          </div>
          <div className="mt-3">
            <div className={`text-3xl font-bold ${colorClass}`}>
              {typeof value === 'number' && value > 999 
                ? `${(value / 1000).toFixed(1)}k` 
                : value
              }
            </div>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
            {trend && (
              <div className="flex items-center mt-2">
                {trend === 'up' ? (
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {trendValue}% from last month
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickActionButton({ icon: Icon, label, onClick, primary = false }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        primary
          ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
          : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
      }`}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </button>
  );
}

function ActivityItem({ activity }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return `${Math.floor(diffInHours * 60)} minutes ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else {
      return `${Math.floor(diffInHours / 24)} days ago`;
    }
  };

  const getActivityIcon = (action) => {
    if (action?.includes('joined') || action?.includes('registered')) {
      return <UserPlusIcon className="h-4 w-4 text-green-600" />;
    }
    if (action?.includes('leave') || action?.includes('request')) {
      return <CalendarIcon className="h-4 w-4 text-orange-600" />;
    }
    if (action?.includes('approved') || action?.includes('accepted')) {
      return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
    }
    return <UsersIcon className="h-4 w-4 text-indigo-600" />;
  };

  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-gradient-to-r hover:from-gray-50 hover:to-indigo-50 rounded-lg transition-all duration-200 cursor-pointer group">
      <div className="flex-shrink-0">
        <div className="h-10 w-10 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
          {getActivityIcon(activity.action)}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 leading-relaxed">
          <span className="font-semibold text-indigo-700">{activity.actor}</span>{' '}
          <span className="text-gray-700">{activity.action}</span>
          {activity.target && (
            <span className="text-gray-600 font-medium"> • {activity.target}</span>
          )}
        </p>
        <div className="flex items-center mt-2">
          <ClockIcon className="h-3 w-3 text-gray-400 mr-1" />
          <p className="text-xs text-gray-500 font-medium">
            {formatTimestamp(activity.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}

const HRDashboard = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [attendanceTrend, setAttendanceTrend] = useState([]);
  const [departmentData, setDepartmentData] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching dashboard data...');

      // Fetch analytics data from the new analytics endpoint
      const analyticsData = await api.get('analytics/dashboard/');

      console.log('✅ Analytics data loaded:', analyticsData);

      const lastTrend = analyticsData.attendance_trends.slice(-1)[0] || {};

      // Transform data for the dashboard components
      setSummary({
        total_employees: analyticsData.employee_stats.total_employees,
        present_today: lastTrend.present || 0,
        pending_leaves: analyticsData.leave_analytics.pending,
        pending_approvals: analyticsData.leave_analytics.pending,
        payroll_this_month: analyticsData.payroll_summary.this_month_payslips,
        on_leave_today: lastTrend.half_day || 0
      });

      setAttendanceTrend(analyticsData.attendance_trends);
      setDepartmentData(analyticsData.department_distribution.map(dept => ({
        name: dept.department__name,
        value: dept.count,
        fill: getDepartmentColor(dept.department__name)
      })));

      // Set empty activities for now (can be enhanced later)
      setActivities([]);

    } catch (error) {
      console.error('❌ Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');

      // Set fallback data
      setSummary({
        total_employees: 0,
        present_today: 0,
        pending_leaves: 0,
        pending_approvals: 0,
        payroll_this_month: 0
      });
      setAttendanceTrend([]);
      setDepartmentData([]);
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'add-employee':
        navigate('/hr/employees');
        break;
      case 'approvals':
        navigate('/hr/employee-approvals');
        break;
      case 'attendance':
        navigate('/hr/attendance');
        break;
      case 'payroll':
        navigate('/hr/payroll');
        break;
      default:
        toast.success(`${action} clicked - Feature coming soon!`);
    }
  };

  const handleExport = async (type, format = 'csv') => {
    try {
      toast.loading(`Exporting ${type} data...`, { id: 'export' });

      let exportPath = '';
      let filename = '';

      switch (type) {
        case 'employees':
          exportPath = 'analytics/export/employees/';
          filename = format === 'excel' ? 'employees.xlsx' : `employees.${format}`;
          break;
        case 'attendance':
          exportPath = 'analytics/export/attendance/';
          filename = format === 'excel' ? 'attendance.xlsx' : `attendance.${format}`;
          break;
        default:
          throw new Error('Unknown export type');
      }

      const envBaseUrl = import.meta.env.VITE_API_URL;
      const defaultBaseUrl = 'http://127.0.0.1:8000/api/v1';
      const apiBaseUrl = envBaseUrl && !envBaseUrl.includes('3000')
        ? envBaseUrl
        : defaultBaseUrl;
      const exportUrl = `${apiBaseUrl.replace(/\/$/, '')}/${exportPath}`;
      const token = localStorage.getItem('token');

      console.log('⬇️ Export URL:', exportUrl);

      const response = await axios.get(exportUrl, {
        responseType: 'blob',
        params: { file_format: format },
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`${type} data exported successfully!`, { id: 'export' });
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export data', { id: 'export' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading HR Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">HR Dashboard</h1>
              <p className="mt-2 text-gray-600">
                Welcome back! Here's what's happening at your company today.
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <QuickActionButton
                icon={PlusIcon}
                label="Add Employee"
                onClick={() => handleQuickAction('add-employee')}
                primary
              />
              <QuickActionButton
                icon={CheckCircleIcon}
                label="Approvals"
                onClick={() => handleQuickAction('approvals')}
              />
              <QuickActionButton
                icon={ClockIcon}
                label="Attendance"
                onClick={() => handleQuickAction('attendance')}
              />
              <QuickActionButton
                icon={CurrencyDollarIcon}
                label="Payroll"
                onClick={() => handleQuickAction('payroll')}
              />
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleExport('employees', 'csv')}
                  className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                  title="Export Employees (CSV)"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  <span>Export CSV</span>
                </button>
                <button
                  onClick={() => handleExport('employees', 'excel')}
                  className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  title="Export Employees (Excel)"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  <span>Export Excel</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Today's Quick Summary */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-6 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-2">📈 Today's Summary</h2>
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  <span>{summary?.present_today || 0} Present</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                  <span>{summary?.on_leave_today || 0} On Leave</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                  <span>{(summary?.total_employees || 0) - (summary?.present_today || 0) - (summary?.on_leave_today || 0)} Absent</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{summary?.total_employees || 0}</div>
              <div className="text-sm opacity-90">Total Employees</div>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <MetricCard
            title="Total Employees"
            value={summary?.total_employees || 0}
            subtitle="Active employees"
            icon={UsersIcon}
            colorClass="text-indigo-600"
            trend="up"
            trendValue="12"
          />
          <MetricCard
            title="Present Today"
            value={summary?.present_today || 0}
            subtitle={`Out of ${summary?.total_employees || 0}`}
            icon={UserPlusIcon}
            colorClass="text-green-600"
            trend="up"
            trendValue="5"
          />
          <MetricCard
            title="Pending Leaves"
            value={summary?.pending_leaves || 0}
            subtitle="Awaiting approval"
            icon={CalendarIcon}
            colorClass="text-orange-500"
          />
          <MetricCard
            title="Pending Approvals"
            value={summary?.pending_approvals || 0}
            subtitle="New registrations"
            icon={ExclamationCircleIcon}
            colorClass="text-red-600"
          />
          <MetricCard
            title="Monthly Payroll"
            value={`$${(summary?.payroll_this_month || 0).toLocaleString()}`}
            subtitle="This month"
            icon={CurrencyDollarIcon}
            colorClass="text-purple-600"
            trend="up"
            trendValue="8"
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Attendance Trend Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-shadow duration-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Attendance Trend</h3>
                <p className="text-sm text-gray-600">Last 30 days overview</p>
              </div>
              <ChartBarIcon className="h-6 w-6 text-gray-400" />
            </div>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={attendanceTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    stroke="#6b7280"
                  />
                  <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="present"
                    stroke="#10B981"
                    strokeWidth={2}
                    dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
                    name="Present"
                  />
                  <Line
                    type="monotone"
                    dataKey="absent"
                    stroke="#EF4444"
                    strokeWidth={2}
                    dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                    name="Absent"
                  />
                  <Line
                    type="monotone"
                    dataKey="half_day"
                    stroke="#F59E0B"
                    strokeWidth={2}
                    dot={{ fill: '#F59E0B', strokeWidth: 2, r: 4 }}
                    name="Half Day"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Department Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-shadow duration-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Department Distribution</h3>
                <p className="text-sm text-gray-600">Employee count by department</p>
              </div>
            </div>
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={departmentData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    innerRadius={30}
                    paddingAngle={2}
                  >
                    {departmentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 space-y-3">
              {departmentData.map((dept, index) => (
                <div key={dept.name} className="flex items-center justify-between text-sm p-2 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-4 h-4 rounded-full shadow-sm"
                      style={{ backgroundColor: dept.fill }}
                    />
                    <span className="text-gray-700 font-medium">{dept.name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-gray-900">{dept.value}</span>
                    <span className="text-xs text-gray-500">emp{dept.value !== 1 ? 's' : ''}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Recent Activities</h3>
              <p className="text-sm text-gray-600">Latest actions and updates</p>
            </div>
            <button
              onClick={fetchDashboardData}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium px-3 py-1 rounded-lg hover:bg-indigo-50 transition-all duration-200"
            >
              Refresh
            </button>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {activities.length === 0 ? (
              <div className="text-center py-8">
                <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No recent activities</p>
              </div>
            ) : (
              activities.map((activity, index) => (
                <ActivityItem key={index} activity={activity} />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Chatbot archived - UI removed */}
    </div>
  );
};

export default HRDashboard;