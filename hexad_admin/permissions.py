from rest_framework.permissions import BasePermission


def user_is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, "role", "") or ""
    return bool(
        user.is_staff
        or user.is_superuser
        or role.lower() in {"admin", "super_admin", "superadmin"}
    )


class IsHexadAdmin(BasePermission):
    message = "Admin privileges are required to access this resource."

    def has_permission(self, request, view):
        return user_is_admin(request.user)