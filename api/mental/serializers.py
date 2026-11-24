from api.common.mixins import UserOwnedSerializer
from rest_framework import serializers
from api.models import (
    CognitiveNote,
    DigitalDetoxBlock,
    SleepWinddownLog,
    StressReset,
)


class DigitalDetoxBlockSerializer(UserOwnedSerializer):
    class Meta:
        model = DigitalDetoxBlock
        fields = ['id', 'user', 'block_label', 'duration_mins', 'screen_time_saved_mins', 'logged_date']


class StressResetSerializer(UserOwnedSerializer):
    class Meta:
        model = StressReset
        fields = ['id', 'user', 'technique', 'stress_before', 'stress_after', 'duration_mins', 'logged_at']

    def validate(self, attrs):
        before = attrs.get('stress_before', getattr(self.instance, 'stress_before', None))
        after = attrs.get('stress_after', getattr(self.instance, 'stress_after', None))
        if before is not None and not (0 <= before <= 10):
            raise serializers.ValidationError({'stress_before': 'Must be between 0 and 10.'})
        if after is not None and not (0 <= after <= 10):
            raise serializers.ValidationError({'stress_after': 'Must be between 0 and 10.'})
        return attrs

class CognitiveNoteSerializer(UserOwnedSerializer):
    class Meta:
        model = CognitiveNote
        fields = ['id', 'user', 'title', 'content', 'tag', 'updated_at']
        read_only_fields = ['updated_at']


class SleepWinddownLogSerializer(UserOwnedSerializer):
    class Meta:
        model = SleepWinddownLog
        fields = ['id', 'user', 'screens_off_time', 'routine_completed', 'log_date']