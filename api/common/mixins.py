from rest_framework import permissions, serializers, viewsets


class UserOwnedSerializer(serializers.ModelSerializer):
    """Ensures `user` is always read-only and bound to the authenticated user."""
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def _validate_user_owned_fk(self, instance, label: str):
        request = self.context.get('request')
        if instance and request and instance.user_id != request.user.id:
            raise serializers.ValidationError(f'{label} does not belong to the authenticated user.')
        return instance


class BaseUserScopedViewSet(viewsets.ModelViewSet):
    """Automatically scopes queries to `request.user` and injects `user` on create."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)