from __future__ import annotations

import json
import urllib.error
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    RegisterSerializer,
)

User = get_user_model()


def _issue_jwt_for_user(user) -> dict:
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'initials': user.initials,
            'auth_provider': user.auth_provider,
            'timezone': user.timezone,
        },
    }


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GoogleAuthView(APIView):
    """POST /api/auth/google/ with {"id_token": "<google_id_token>"}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'detail': 'id_token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                payload = json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, ValueError):
            return Response({'detail': 'Invalid Google token.'}, status=status.HTTP_401_UNAUTHORIZED)

        expected_aud = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None)
        if expected_aud and payload.get('aud') != expected_aud:
            return Response({'detail': 'Token audience mismatch.'}, status=status.HTTP_401_UNAUTHORIZED)

        if str(payload.get('email_verified', '')).lower() != 'true' or not payload.get('email'):
            return Response({'detail': 'Google email not verified.'}, status=status.HTTP_401_UNAUTHORIZED)

        email = User.objects.normalize_email(payload['email'])
        full_name = (payload.get('name') or email.split('@')[0]).strip()
        initials = ''.join(part[0].upper() for part in full_name.split()[:2])

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'initials': initials,
                'auth_provider': User.AuthProvider.GOOGLE,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])

        return Response(_issue_jwt_for_user(user), status=status.HTTP_200_OK)