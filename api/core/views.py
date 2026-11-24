from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    DailyHabit,
    HabitLog,
    PillarCheckin,
    PillarGoal,
    UserPillarFocus,
    UserStreak,
    WeeklySnapshot,
)
from .serializers import (
    DailyHabitSerializer,
    HabitLogSerializer,
    PillarCheckinSerializer,
    PillarGoalSerializer,
    UserPillarFocusSerializer,
    UserStreakSerializer,
    WeeklySnapshotSerializer,
)


class UserPillarFocusViewSet(BaseUserScopedViewSet):
    queryset = UserPillarFocus.objects.all()
    serializer_class = UserPillarFocusSerializer


class UserStreakViewSet(BaseUserScopedViewSet):
    queryset = UserStreak.objects.all()
    serializer_class = UserStreakSerializer
    http_method_names = ['get', 'head', 'options']


class PillarGoalViewSet(BaseUserScopedViewSet):
    queryset = PillarGoal.objects.all()
    serializer_class = PillarGoalSerializer
    filterset_fields = ['pillar_slug', 'cadence', 'status']


class PillarCheckinViewSet(BaseUserScopedViewSet):
    queryset = PillarCheckin.objects.select_related('goal')
    serializer_class = PillarCheckinSerializer
    filterset_fields = ['pillar_slug', 'goal']


class DailyHabitViewSet(BaseUserScopedViewSet):
    queryset = DailyHabit.objects.all()
    serializer_class = DailyHabitSerializer
    filterset_fields = ['pillar_slug', 'is_active']


class HabitLogViewSet(BaseUserScopedViewSet):
    queryset = HabitLog.objects.select_related('habit')
    serializer_class = HabitLogSerializer
    filterset_fields = ['habit', 'log_date', 'completed']


class WeeklySnapshotViewSet(BaseUserScopedViewSet):
    queryset = WeeklySnapshot.objects.all()
    serializer_class = WeeklySnapshotSerializer
    filterset_fields = ['pillar_slug', 'week_start_date']
    http_method_names = ['get', 'head', 'options']