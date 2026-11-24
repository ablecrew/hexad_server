from api.common.mixins import UserOwnedSerializer
from api.models import (
    Boundary,
    EmotionalTrigger,
    JournalEntry,
    Relationship,
)


class JournalEntrySerializer(UserOwnedSerializer):
    class Meta:
        model = JournalEntry
        fields = ['id', 'user', 'prompt', 'body', 'mood_label', 'mood_score', 'created_at']
        read_only_fields = ['created_at']


class RelationshipSerializer(UserOwnedSerializer):
    class Meta:
        model = Relationship
        fields = ['id', 'user', 'person_name', 'circle', 'target_cadence_days', 'last_connected_at']


class BoundarySerializer(UserOwnedSerializer):
    class Meta:
        model = Boundary
        fields = ['id', 'user', 'title', 'context', 'adherence_pct', 'is_active']


class EmotionalTriggerSerializer(UserOwnedSerializer):
    class Meta:
        model = EmotionalTrigger
        fields = ['id', 'user', 'trigger_name', 'pattern_note', 'intensity', 'coping_response', 'occurred_at']