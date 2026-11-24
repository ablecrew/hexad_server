from api.common.mixins import UserOwnedSerializer
from rest_framework import serializers
from api.models import (
    CardioStepLog,
    EnergyCheckin,
    NutritionHydrationLog,
    SleepLog,
)
class SleepLogSerializer(UserOwnedSerializer):
    class Meta:
        model = SleepLog
        fields = ['id', 'user', 'bedtime', 'wake_time', 'duration_hrs', 'recovery_score']

    def validate(self, attrs):
        bedtime = attrs.get('bedtime', getattr(self.instance, 'bedtime', None))
        wake_time = attrs.get('wake_time', getattr(self.instance, 'wake_time', None))
        if bedtime and wake_time and wake_time <= bedtime:
            raise serializers.ValidationError({'wake_time': 'wake_time must be after bedtime.'})
        return attrs


class NutritionHydrationLogSerializer(UserOwnedSerializer):
    class Meta:
        model = NutritionHydrationLog
        fields = ['id', 'user', 'log_date', 'water_liters', 'meals_on_plan', 'notes']


class EnergyCheckinSerializer(UserOwnedSerializer):
    class Meta:
        model = EnergyCheckin
        fields = ['id', 'user', 'energy_level', 'time_of_day', 'logged_at']


class CardioStepLogSerializer(UserOwnedSerializer):
    class Meta:
        model = CardioStepLog
        fields = ['id', 'user', 'activity_type', 'steps_count', 'distance_km', 'duration_mins', 'logged_date']