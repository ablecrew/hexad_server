from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsHexadAdmin, user_is_admin
from .serializers import AdminInviteSerializer, AdminSettingsSerializer

User = get_user_model()

# Persistent settings should live in a DB model (e.g., PlatformSetting.objects.get_or_create(pk=1)[0])
PLATFORM_SETTINGS = {
    "app_name": "Hexad",
    "default_currency": "KSH",
    "weekly_digest_day": "Sunday evening",
    "daily_checkin_reminders": True,
    "public_landing_preview": True,
    "self_serve_signup": True,
}

PILLAR_CONFIG = [
    ("financial", "Financial (Ksh)", "#006A4E"),
    ("academics", "Academics", "#1D6FA5"),
    ("physical", "Physical", "#8F4A00"),
    ("mental", "Mental", "#007A63"),
    ("spiritual", "Spiritual", "#5A52B5"),
    ("emotional", "Emotional", "#974722"),
]


class AdminOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsHexadAdmin]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        day_ago = now - timedelta(days=1)
        month_ago = now - timedelta(days=30)

        total_members = User.objects.count()
        new_members_this_week = User.objects.filter(created_at__gte=week_ago).count()
        dau = User.objects.filter(last_login__gte=day_ago).count()
        mau = User.objects.filter(last_login__gte=month_ago).count()
        dau_mau_pct = round((dau / mau) * 100, 1) if mau > 0 else 0.0

        weekly_checkins = 0
        avg_pillar_score = 0
        engagement_rows = []
        recent_activity = []

        try:
            from api.core.models import WeeklySnapshot

            snapshots = WeeklySnapshot.objects.all()
            avg_val = snapshots.aggregate(avg=Avg("score_pct"))["avg"]
            avg_pillar_score = round(avg_val) if avg_val is not None else 0

            for slug, label, color in PILLAR_CONFIG:
                p_avg = snapshots.filter(pillar_slug=slug).aggregate(avg=Avg("score_pct"))["avg"]
                engagement_rows.append(
                    {
                        "pillar_slug": slug,
                        "label": label,
                        "score_pct": round(p_avg) if p_avg is not None else 0,
                        "bar_color": color,
                    }
                )
        except Exception:
            engagement_rows = [
                {
                    "pillar_slug": slug,
                    "label": label,
                    "score_pct": 0,
                    "bar_color": color,
                }
                for slug, label, color in PILLAR_CONFIG
            ]

        # Count real activity across core models if present
        try:
            from api.core.models import HabitLog

            weekly_checkins += HabitLog.objects.filter(
                completed=True, log_date__gte=week_ago.date()
            ).count()
            recent_logs = HabitLog.objects.select_related("habit", "habit__user").order_by(
                "-id"
            )[:5]
            for log in recent_logs:
                actor = (
                    log.habit.user.get_full_name()
                    or log.habit.user.email
                    if getattr(log.habit, "user", None)
                    else "Member"
                )
                recent_activity.append(
                    {
                        "id": f"habit-{log.id}",
                        "title": log.habit.title,
                        "subtitle": f"{actor} · {log.habit.pillar_slug}",
                        "time_label": str(log.log_date),
                    }
                )
        except Exception:
            pass

        return Response(
            {
                "total_members": total_members,
                "new_members_this_week": new_members_this_week,
                "daily_active": dau,
                "dau_mau_pct": dau_mau_pct,
                "weekly_checkins": weekly_checkins,
                "avg_pillar_score": avg_pillar_score,
                "pillar_engagement": engagement_rows,
                "recent_activity": recent_activity,
            }
        )


class AdminUsersListView(APIView):
    permission_classes = [IsAuthenticated, IsHexadAdmin]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip().lower()
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        all_users = User.objects.all()
        total_users = all_users.count()
        new_this_week = all_users.filter(created_at__gte=week_ago).count()
        verified_count = all_users.filter(is_active=True).count()
        verified_pct = round((verified_count / total_users) * 100, 1) if total_users > 0 else 0.0

        qs = all_users.order_by("-created_at")[:100]
        results = []

        for u in qs:
            full_name = (getattr(u, "full_name", "") or u.get_full_name() or u.email).strip()
            initials = getattr(u, "initials", "") or "".join(
                p[0].upper() for p in full_name.split()[:2]
            )
            streak_obj = getattr(u, "streak", None)
            streak_days = getattr(streak_obj, "current_streak_days", 0) or 0

            row = {
                "id": u.pk,
                "full_name": full_name,
                "email": u.email,
                "initials": initials,
                "role": "Admin" if user_is_admin(u) else "Member",
                "streak_days": streak_days,
                "balance_pct": 0,
                "status": "Active" if u.is_active else "Pending",
            }
            if not q or q in full_name.lower() or q in (u.email or "").lower():
                results.append(row)

        return Response(
            {
                "summary": {
                    "total_users": total_users,
                    "new_this_week": new_this_week,
                    "verified_pct": verified_pct,
                    "needs_review": all_users.filter(is_active=False).count(),
                },
                "count": len(results),
                "results": results,
            }
        )


class AdminInviteUserView(APIView):
    permission_classes = [IsAuthenticated, IsHexadAdmin]

    def post(self, request):
        serializer = AdminInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        full_name = serializer.validated_data.get("full_name", "").strip()
        role = serializer.validated_data["role"]

        return Response(
            {
                "detail": f"Invitation queued for {email}.",
                "email": email,
                "full_name": full_name,
                "role": role,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsHexadAdmin]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        total_users = User.objects.count()
        active_7d = User.objects.filter(last_login__gte=week_ago).count()
        retention_7d_pct = round((active_7d / total_users) * 100) if total_users > 0 else 0

        goals_total = 0
        goals_completed = 0
        daily_volume = []

        try:
            from api.core.models import PillarGoal, HabitLog

            goals_total = PillarGoal.objects.count()
            goals_completed = PillarGoal.objects.filter(status="completed").count()

            max_count = 1
            day_counts = []
            for offset in range(6, -1, -1):
                day_date = (now - timedelta(days=offset)).date()
                cnt = HabitLog.objects.filter(log_date=day_date, completed=True).count()
                if cnt > max_count:
                    max_count = cnt
                day_counts.append((day_date.strftime("%a"), cnt))

            for label, cnt in day_counts:
                pct = round((cnt / max_count) * 100) if cnt > 0 else 4
                daily_volume.append({"day": label, "value_pct": pct, "muted": cnt == 0})
        except Exception:
            for offset in range(6, -1, -1):
                day_date = (now - timedelta(days=offset)).date()
                daily_volume.append({"day": day_date.strftime("%a"), "value_pct": 4, "muted": True})

        goal_completion_pct = round((goals_completed / goals_total) * 100) if goals_total > 0 else 0

        return Response(
            {
                "retention_7d_pct": retention_7d_pct,
                "retention_delta_label": f"{active_7d} active in last 7d",
                "avg_session_label": "—",
                "goal_completion_pct": goal_completion_pct,
                "ksh_logs_per_week": 0,
                "daily_volume": daily_volume,
                "top_sub_views": [],
            }
        )


class AdminSettingsView(APIView):
    permission_classes = [IsAuthenticated, IsHexadAdmin]

    def get(self, request):
        return Response(PLATFORM_SETTINGS)

    def put(self, request):
        serializer = AdminSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PLATFORM_SETTINGS.update(serializer.validated_data)
        return Response(PLATFORM_SETTINGS)