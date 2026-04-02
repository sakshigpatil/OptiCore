import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const REPORT_TYPES = [
  { value: 'employees', label: 'Employees' },
  { value: 'attendance', label: 'Attendance' },
];

const FILE_FORMATS = [
  { value: 'csv', label: 'CSV' },
  { value: 'excel', label: 'Excel (.xlsx)' },
];

const CustomReports = () => {
  const [form, setForm] = useState({
    report_type: 'employees',
    file_format: 'csv',
    start_date: '',
    end_date: '',
  });
  const [loading, setLoading] = useState(false);

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleGenerate = async (event) => {
    event.preventDefault();
    try {
      setLoading(true);
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const reportUrl = `${apiBaseUrl.replace(/\/$/, '')}/analytics/custom-report/`;
      const token = localStorage.getItem('token');

      const payload = {
        report_type: form.report_type,
        file_format: form.file_format,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
      };

      const response = await axios.post(reportUrl, payload, {
        responseType: 'blob',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      const extension = form.file_format === 'excel' ? 'xlsx' : form.file_format;
      const filename = `custom_${form.report_type}.${extension}`;
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Report generated');
    } catch (error) {
      console.error('Failed to generate report', error);
      toast.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Custom Reports</h1>
          <p className="mt-2 text-gray-600">Build and download one-off HR reports.</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            {form.report_type === 'attendance' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={form.start_date}
                    onChange={(e) => updateField('start_date', e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={form.end_date}
                    onChange={(e) => updateField('end_date', e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                  />
                </div>
              </>
            )}
            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-60"
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CustomReports;
