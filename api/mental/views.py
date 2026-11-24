from django.db.models import Avg, F, Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    CognitiveNote,
    DigitalDetoxBlock,
    SleepWinddownLog,
    StressReset,
)
from .serializers import (
    CognitiveNoteSerializer,
    DigitalDetoxBlockSerializer,
    SleepWinddownLogSerializer,
    StressResetSerializer,
)


class DigitalDetoxBlockViewSet(BaseUserScopedViewSet):
    queryset = DigitalDetoxBlock.objects.all()
    serializer_class = DigitalDetoxBlockSerializer
    filterset_fields = ['logged_date']
    search_fields = ['block_label']
    ordering = ['-logged_date']


class StressResetViewSet(BaseUserScopedViewSet):
    queryset = StressReset.objects.all()
    serializer_class = StressResetSerializer
    search_fields = ['technique']
    ordering = ['-logged_at']


class CognitiveNoteViewSet(BaseUserScopedViewSet):
    queryset = CognitiveNote.objects.all()
    serializer_class = CognitiveNoteSerializer
    filterset_fields = ['tag']
    search_fields = ['title', 'content']
    ordering = ['-updated_at']


class SleepWinddownLogViewSet(BaseUserScopedViewSet):
    queryset = SleepWinddownLog.objects.all()
    serializer_class = SleepWinddownLogSerializer
    filterset_fields = ['log_date', 'routine_completed']
    ordering = ['-log_date']


class MentalSummaryView(APIView):
    """GET /api/mental/summary/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        detox_totals = DigitalDetoxBlock.objects.filter(user=user).aggregate(
            detox_mins=Sum('duration_mins'),
            saved_mins=Sum('screen_time_saved_mins'),
        )
        avg_stress_drop = StressReset.objects.filter(user=user).aggregate(
            avg_drop=Avg(F('stress_before') - F('stress_after'))
        )['avg_drop']

        return Response({
            'total_detox_mins': detox_totals['detox_mins'] or 0,
            'total_screen_time_saved_mins': detox_totals['saved_mins'] or 0,
            'average_stress_reduction': round(avg_stress_drop, 2) if avg_stress_drop is not None else None,
            'cognitive_notes_count': CognitiveNote.objects.filter(user=user).count(),
            'winddown_completed_days': SleepWinddownLog.objects.filter(
                user=user, routine_completed=True
            ).count(),
        })