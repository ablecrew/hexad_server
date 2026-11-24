from api.common.mixins import UserOwnedSerializer
from api.models import (
    BreathSession,
    CoreValue,
    GratitudeEntry,
    SacredReading,
)


class GratitudeEntrySerializer(UserOwnedSerializer):
    class Meta:
        model = GratitudeEntry
        fields = ['id', 'user', 'entry_text', 'category', 'logged_date']


class CoreValueSerializer(UserOwnedSerializer):
    class Meta:
        model = CoreValue
        fields = ['id', 'user', 'value_name', 'purpose_statement', 'alignment_score']


class SacredReadingSerializer(UserOwnedSerializer):
    class Meta:
        model = SacredReading
        fields = ['id', 'user', 'source_title', 'passage_ref', 'reflection', 'read_at']


class BreathSessionSerializer(UserOwnedSerializer):
    class Meta:
        model = BreathSession
        fields = ['id', 'user', 'pattern', 'duration_mins', 'completed_at']