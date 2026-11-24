from django.db.models import Avg
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    Boundary,
    EmotionalTrigger,
    JournalEntry,
    Relationship,
)
from .serializers import (
    BoundarySerializer,
    EmotionalTriggerSerializer,
    JournalEntrySerializer,
    RelationshipSerializer,
)


class JournalEntryViewSet(BaseUserScopedViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    filterset_fields = ['mood_label']
    search_fields = ['prompt', 'body']
    ordering = ['-created_at']


class RelationshipViewSet(BaseUserScopedViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    filterset_fields = ['circle']
    search_fields = ['person_name']


class BoundaryViewSet(BaseUserScopedViewSet):
    queryset = Boundary.objects.all()
    serializer_class = BoundarySerializer
    filterset_fields = ['is_active']
    search_fields = ['title', 'context']


class EmotionalTriggerViewSet(BaseUserScopedViewSet):
    queryset = EmotionalTrigger.objects.all()
    serializer_class = EmotionalTriggerSerializer
    filterset_fields = ['intensity']
    search_fields = ['trigger_name', 'pattern_note', 'coping_response']
    ordering = ['-occurred_at']


class EmotionalSummaryView(APIView):
    """GET /api/emotional/summary/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        avg_mood = JournalEntry.objects.filter(user=user).aggregate(avg=Avg('mood_score'))['avg']
        avg_adherence = Boundary.objects.filter(user=user, is_active=True).aggregate(
            avg=Avg('adherence_pct')
        )['avg']

        return Response({
            'journal_entries_count': JournalEntry.objects.filter(user=user).count(),
            'average_mood_score': round(avg_mood, 2) if avg_mood is not None else None,
            'active_boundaries_count': Boundary.objects.filter(user=user, is_active=True).count(),
            'average_boundary_adherence_pct': round(avg_adherence, 2) if avg_adherence is not None else None,
            'relationships_count': Relationship.objects.filter(user=user).count(),
        })