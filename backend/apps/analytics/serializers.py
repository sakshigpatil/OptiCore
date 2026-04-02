from rest_framework import serializers
from .models import ScheduledReport


class ScheduledReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = [
            'id',
            'owner',
            'name',
            'report_type',
            'file_format',
            'schedule_type',
            'day_of_week',
            'day_of_month',
            'time_of_day',
            'is_active',
            'next_run_at',
            'last_run_at',
            'last_status',
            'last_message',
            'last_report_file',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'owner',
            'next_run_at',
            'last_run_at',
            'last_status',
            'last_message',
            'last_report_file',
            'created_at',
            'updated_at',
        ]
