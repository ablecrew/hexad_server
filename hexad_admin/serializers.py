from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AdminInviteSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["Member", "Admin"], default="Member")


class AdminSettingsSerializer(serializers.Serializer):
    app_name = serializers.CharField(max_length=120)
    default_currency = serializers.ChoiceField(choices=["KSH", "USD", "EUR"])
    weekly_digest_day = serializers.CharField(max_length=60)
    daily_checkin_reminders = serializers.BooleanField()
    public_landing_preview = serializers.BooleanField()
    self_serve_signup = serializers.BooleanField()