from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from apps.analytics.models import ScheduledReport
from apps.analytics.reporting import generate_report_bytes
from apps.analytics.views import get_user_permissions
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = 'Run due scheduled reports and store the output files.'

    def handle(self, *args, **options):
        now = timezone.now()
        due_reports = ScheduledReport.objects.filter(is_active=True, next_run_at__lte=now)

        for report in due_reports:
            try:
                permissions = get_user_permissions(report.owner)
                buffer = generate_report_bytes(report.report_type, report.file_format, report.owner, permissions)

                timestamp = now.strftime('%Y%m%d_%H%M%S')
                ext = 'xlsx' if report.file_format == 'excel' else 'csv'
                filename = f"{report.report_type}_{report.owner_id}_{timestamp}.{ext}"

                report.last_report_file.save(filename, ContentFile(buffer.getvalue()), save=False)
                report.last_run_at = now
                report.last_status = 'success'
                report.last_message = 'Report generated successfully'
                report.next_run_at = report.compute_next_run(now)
                report.save()

                Notification.objects.create(
                    recipient=report.owner,
                    title=f"Scheduled report ready: {report.name}",
                    message=f"Your {report.report_type} report is ready.",
                    notification_type='INFO',
                    action_url=report.last_report_file.url if report.last_report_file else None
                )
            except Exception as exc:
                report.last_run_at = now
                report.last_status = 'failed'
                report.last_message = str(exc)
                report.next_run_at = report.compute_next_run(now)
                report.save()

                Notification.objects.create(
                    recipient=report.owner,
                    title=f"Scheduled report failed: {report.name}",
                    message=str(exc),
                    notification_type='ERROR'
                )

        self.stdout.write(self.style.SUCCESS(f"Processed {due_reports.count()} scheduled reports."))
