import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';

const REPORT_TYPES = [
  { value: 'employees', label: 'Employees' },
  { value: 'attendance', label: 'Attendance' },
];

const FILE_FORMATS = [
  { value: 'csv', label: 'CSV' },
  { value: 'excel', label: 'Excel (.xlsx)' },
];

const SCHEDULE_TYPES = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

const ScheduledReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: '',
    report_type: 'employees',
    file_format: 'csv',
    schedule_type: 'weekly',
    day_of_week: 0,
    day_of_month: 1,
    time_of_day: '09:00:00',
    is_active: true,
  });

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await api.get('analytics/scheduled-reports/');
      setReports(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error('Failed to load scheduled reports', error);
      toast.error('Failed to load scheduled reports');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    try {
      setSubmitting(true);
      const payload = {
        ...form,
        day_of_week: form.schedule_type === 'weekly' ? Number(form.day_of_week) : null,
        day_of_month: form.schedule_type === 'monthly' ? Number(form.day_of_month) : null,
      };
      await api.post('analytics/scheduled-reports/', payload);
      toast.success('Scheduled report created');
      setForm((prev) => ({
        ...prev,
        name: '',
      }));
      fetchReports();
    } catch (error) {
      console.error('Failed to create scheduled report', error);
      toast.error('Failed to create scheduled report');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRunNow = async (reportId) => {
    try {
      toast.loading('Generating report...', { id: 'run-now' });
      const response = await api.post(`analytics/scheduled-reports/${reportId}/run_now/`);
      toast.success('Report generated', { id: 'run-now' });
      if (response?.file) {
        window.open(response.file, '_blank');
      }
      fetchReports();
    } catch (error) {
      console.error('Failed to run report', error);
      toast.error('Failed to run report', { id: 'run-now' });
    }
  };

  const handleDelete = async (reportId) => {
    try {
      await api.delete(`analytics/scheduled-reports/${reportId}/`);
      toast.success('Scheduled report deleted');
      fetchReports();
    } catch (error) {
      console.error('Failed to delete report', error);
      toast.error('Failed to delete report');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Scheduled Reports</h1>
          <p className="mt-2 text-gray-600">Create automated HR reports and run them on a schedule.</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Create new schedule</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="Weekly Employees Report"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
              <select
                value={form.report_type}
                onChange={(e) => updateField('report_type', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              >
                {REPORT_TYPES.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">File Format</label>
              <select
                value={form.file_format}
                onChange={(e) => updateField('file_format', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              >
                {FILE_FORMATS.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Schedule</label>
              <select
                value={form.schedule_type}
                onChange={(e) => updateField('schedule_type', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              >
                {SCHEDULE_TYPES.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </div>
            {form.schedule_type === 'weekly' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Day of Week</label>
                <select
                  value={form.day_of_week}
                  onChange={(e) => updateField('day_of_week', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2"
                >
                  {DAYS_OF_WEEK.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </div>
            )}
            {form.schedule_type === 'monthly' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Day of Month</label>
                <input
                  type="number"
                  min="1"
                  max="28"
                  value={form.day_of_month}
                  onChange={(e) => updateField('day_of_month', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time of Day</label>
              <input
                type="time"
                value={form.time_of_day}
                onChange={(e) => updateField('time_of_day', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                required
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => updateField('is_active', e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <span className="text-sm text-gray-700">Active</span>
            </div>
            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-60"
              >
                {submitting ? 'Creating...' : 'Create Schedule'}
              </button>
            </div>
          </form>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Existing schedules</h2>
            <button
              onClick={fetchReports}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="text-gray-600">Loading schedules...</div>
          ) : reports.length === 0 ? (
            <div className="text-gray-600">No scheduled reports yet.</div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div key={report.id} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <h3 className="font-semibold text-gray-900">{report.name}</h3>
                      <p className="text-sm text-gray-600">
                        {report.report_type} • {report.file_format} • {report.schedule_type}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Next run: {report.next_run_at || 'Not scheduled'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleRunNow(report.id)}
                        className="px-3 py-1 rounded-lg bg-emerald-600 text-white text-sm hover:bg-emerald-700"
                      >
                        Run now
                      </button>
                      <button
                        onClick={() => handleDelete(report.id)}
                        className="px-3 py-1 rounded-lg bg-gray-100 text-gray-700 text-sm hover:bg-gray-200"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScheduledReports;
