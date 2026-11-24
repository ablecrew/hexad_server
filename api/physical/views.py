from django.db.models import Avg, Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    CardioStepLog,
    EnergyCheckin,
    NutritionHydrationLog,
    SleepLog,
)
from .serializers import (
    CardioStepLogSerializer,
    EnergyCheckinSerializer,
    NutritionHydrationLogSerializer,
    SleepLogSerializer,
)


class SleepLogViewSet(BaseUserScopedViewSet):
    queryset = SleepLog.objects.all()
    serializer_class = SleepLogSerializer
    ordering = ['-wake_time']


class NutritionHydrationLogViewSet(BaseUserScopedViewSet):
    queryset = NutritionHydrationLog.objects.all()
    serializer_class = NutritionHydrationLogSerializer
    filterset_fields = ['log_date']
    ordering = ['-log_date']


class EnergyCheckinViewSet(BaseUserScopedViewSet):
    queryset = EnergyCheckin.objects.all()
    serializer_class = EnergyCheckinSerializer
    filterset_fields = ['time_of_day']
    ordering = ['-logged_at']


class CardioStepLogViewSet(BaseUserScopedViewSet):
    queryset = CardioStepLog.objects.all()
    serializer_class = CardioStepLogSerializer
    filterset_fields = ['activity_type', 'logged_date']
    ordering = ['-logged_date']


class PhysicalSummaryView(APIView):
    """GET /api/physical/summary/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        sleep_stats = SleepLog.objects.filter(user=user).aggregate(
            avg_hrs=Avg('duration_hrs'),
            avg_recovery=Avg('recovery_score'),
        )
        cardio_stats = CardioStepLog.objects.filter(user=user).aggregate(
            total_steps=Sum('steps_count'),
            total_km=Sum('distance_km'),
        )
        avg_water = NutritionHydrationLog.objects.filter(user=user).aggregate(
            avg_water=Avg('water_liters')
        )['avg_water']

        return Response({
            'average_sleep_hrs': round(sleep_stats['avg_hrs'], 2) if sleep_stats['avg_hrs'] is not None else None,
            'average_recovery_score': round(sleep_stats['avg_recovery'], 2) if sleep_stats['avg_recovery'] is not None else None,
            'total_steps': cardio_stats['total_steps'] or 0,
            'total_distance_km': cardio_stats['total_km'] or 0,
            'average_water_liters': round(avg_water, 2) if avg_water is not None else None,
        })