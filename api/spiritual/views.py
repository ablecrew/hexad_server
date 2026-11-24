from django.db.models import Avg, Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    BreathSession,
    CoreValue,
    GratitudeEntry,
    SacredReading,
)
from .serializers import (
    BreathSessionSerializer,
    CoreValueSerializer,
    GratitudeEntrySerializer,
    SacredReadingSerializer,
)


class GratitudeEntryViewSet(BaseUserScopedViewSet):
    queryset = GratitudeEntry.objects.all()
    serializer_class = GratitudeEntrySerializer
    filterset_fields = ['category', 'logged_date']
    search_fields = ['entry_text']
    ordering = ['-logged_date']


class CoreValueViewSet(BaseUserScopedViewSet):
    queryset = CoreValue.objects.all()
    serializer_class = CoreValueSerializer
    search_fields = ['value_name', 'purpose_statement']


class SacredReadingViewSet(BaseUserScopedViewSet):
    queryset = SacredReading.objects.all()
    serializer_class = SacredReadingSerializer
    search_fields = ['source_title', 'passage_ref', 'reflection']
    ordering = ['-read_at']


class BreathSessionViewSet(BaseUserScopedViewSet):
    queryset = BreathSession.objects.all()
    serializer_class = BreathSessionSerializer
    filterset_fields = ['pattern']
    ordering = ['-completed_at']


class SpiritualSummaryView(APIView):
    """GET /api/spiritual/summary/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        avg_alignment = CoreValue.objects.filter(user=user).aggregate(avg=Avg('alignment_score'))['avg']
        total_breath_mins = BreathSession.objects.filter(user=user).aggregate(
            total=Sum('duration_mins')
        )['total'] or 0

        return Response({
            'gratitude_entries_count': GratitudeEntry.objects.filter(user=user).count(),
            'average_value_alignment_pct': round(avg_alignment, 2) if avg_alignment is not None else None,
            'sacred_readings_count': SacredReading.objects.filter(user=user).count(),
            'total_breath_mins': total_breath_mins,
        })