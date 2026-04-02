from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta

from .models import Holiday
from .serializers import HolidaySerializer


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['date', 'is_recurring', 'country']
    search_fields = ['name', 'description']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Return upcoming holidays (next 30 days by default)"""
        start = date.today()
        end_param = request.query_params.get('end')
        if end_param:
            try:
                end = date.fromisoformat(end_param)
            except Exception:
                end = start + timedelta(days=30)
        else:
            end = start + timedelta(days=30)

        qs = self.get_queryset().filter(date__range=[start, end])
        serializer = self.get_serializer(qs, many=True)
        return Response({'success': True, 'data': serializer.data})
