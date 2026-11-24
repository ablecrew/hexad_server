from api.common.mixins import UserOwnedSerializer
from api.models import (
    DailyHabit,
    HabitLog,
    PillarCheckin,
    PillarGoal,
    UserPillarFocus,
    UserStreak,
    WeeklySnapshot,
)


class UserPillarFocusSerializer(UserOwnedSerializer):
    class Meta:
        model = UserPillarFocus
        fields = ['id', 'user', 'pillar_slug', 'is_active', 'target_weight']


class UserStreakSerializer(UserOwnedSerializer):
    class Meta:
        model = UserStreak
        fields = ['id', 'user', 'current_streak_days', 'longest_streak_days', 'last_checkin_date']
        read_only_fields = ['current_streak_days', 'longest_streak_days', 'last_checkin_date']


class PillarGoalSerializer(UserOwnedSerializer):
    class Meta:
        model = PillarGoal
        fields = [
            'id', 'user', 'pillar_slug', 'subtab_slug', 'title',
            'cadence', 'target_value', 'current_value', 'unit', 'status', 'due_date', 'created_at',
        ]
        read_only_fields = ['created_at']


class PillarCheckinSerializer(UserOwnedSerializer):
    class Meta:
        model = PillarCheckin
        fields = [
            'id', 'user', 'pillar_slug', 'subtab_slug', 'goal',
            'title', 'note', 'metric_label', 'logged_at',
        ]
        read_only_fields = ['logged_at']

    def validate_goal(self, goal):
        return self._validate_user_owned_fk(goal, 'Goal')


class DailyHabitSerializer(UserOwnedSerializer):
    class Meta:
        model = DailyHabit
        fields = ['id', 'user', 'pillar_slug', 'title', 'scheduled_time', 'is_active']


class HabitLogSerializer(UserOwnedSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'user', 'log_date', 'completed', 'completed_at']

    def validate_habit(self, habit):
        return self._validate_user_owned_fk(habit, 'Habit')


class WeeklySnapshotSerializer(UserOwnedSerializer):
    class Meta:
        model = WeeklySnapshot
        fields = ['id', 'user', 'week_start_date', 'pillar_slug', 'score_pct', 'checkins_count', 'streak_days']