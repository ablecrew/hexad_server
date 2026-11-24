from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from hexad_admin.permissions import user_is_admin

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password', 'timezone']
        read_only_fields = ['id']

    def create(self, validated_data):
        full_name = validated_data['full_name'].strip()
        initials = ''.join(part[0].upper() for part in full_name.split()[:2])
        return User.objects.create_user(
            email=validated_data['email'],
            full_name=full_name,
            password=validated_data['password'],
            initials=initials,
            timezone=validated_data.get('timezone', 'Africa/Nairobi'),
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['is_staff'] = bool(user.is_staff)
        token['is_superuser'] = bool(user.is_superuser)
        token['is_admin'] = user_is_admin(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'full_name': self.user.full_name,
            'initials': self.user.initials,
            'timezone': self.user.timezone,
            'is_staff': bool(self.user.is_staff),
            'is_superuser': bool(self.user.is_superuser),
            'is_admin': user_is_admin(self.user),
        }
        return data


class ProfileSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'initials',
            'auth_provider',
            'timezone',
            'created_at',
            'is_staff',
            'is_superuser',
            'is_admin',
        ]
        read_only_fields = [
            'id',
            'email',
            'auth_provider',
            'created_at',
            'is_staff',
            'is_superuser',
            'is_admin',
        ]

    def get_is_admin(self, obj):
        return user_is_admin(obj)