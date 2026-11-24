from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from api.models import (
    FinancialTransaction,
    PillarGoal,
    SpendingBudget,
    UserStreak,
    WeeklySnapshot,
)


def get_user_local_date(user, dt=None) -> date:
    dt = dt or timezone.now()
    try:
        tz = ZoneInfo(user.timezone or 'Africa/Nairobi')
    except Exception:
        tz = ZoneInfo('Africa/Nairobi')
    return timezone.localtime(dt, tz).date()


def get_week_start(local_date: date) -> date:
    """Monday of the week containing local_date."""
    return local_date - timedelta(days=local_date.weekday())


def calculate_weekly_score(user, pillar_slug: str, week_start: date, checkins_count: int) -> int:
    """
    Example scoring formula (0-100):
    - Up to 60 pts from weekly check-ins/activity (10 pts each, capped at 6)
    - Up to 40 pts from average progress on active/completed goals in that pillar
    """
    activity_pts = min(60, checkins_count * 10)

    goals = PillarGoal.objects.filter(user=user, pillar_slug=pillar_slug)
    goal_pts = 0
    if goals.exists():
        ratios = []
        for g in goals:
            if g.target_value and g.target_value > 0:
                ratio = min(Decimal('1.0'), max(Decimal('0.0'), g.current_value / g.target_value))
                ratios.append(ratio)
        if ratios:
            avg_ratio = sum(ratios) / Decimal(len(ratios))
            goal_pts = int(round(float(avg_ratio) * 40))

    return min(100, activity_pts + goal_pts)


@transaction.atomic
def record_checkin_activity(
    user,
    pillar_slug: str,
    goal: PillarGoal | None = None,
    occurred_at=None,
    goal_increment: Decimal | None = None,
):
    local_today = get_user_local_date(user, occurred_at)

    # 1. Update streak at most once per local day
    streak, _ = UserStreak.objects.select_for_update().get_or_create(user=user)
    if streak.last_checkin_date != local_today:
        if streak.last_checkin_date == local_today - timedelta(days=1):
            streak.current_streak_days += 1
        else:
            streak.current_streak_days = 1
        streak.longest_streak_days = max(streak.longest_streak_days, streak.current_streak_days)
        streak.last_checkin_date = local_today
        streak.save(update_fields=['current_streak_days', 'longest_streak_days', 'last_checkin_date'])

    # 2. Increment linked goal only when explicitly requested
    if goal and goal_increment is not None and goal.status == PillarGoal.Status.ACTIVE:
        PillarGoal.objects.filter(pk=goal.pk).update(
            current_value=F('current_value') + goal_increment
        )
        goal.refresh_from_db()
        if goal.current_value >= goal.target_value:
            PillarGoal.objects.filter(pk=goal.pk).update(status=PillarGoal.Status.COMPLETED)

    # 3. Update weekly snapshot for the pillar
    week_start = get_week_start(local_today)
    snapshot, _ = WeeklySnapshot.objects.select_for_update().get_or_create(
        user=user,
        week_start_date=week_start,
        pillar_slug=pillar_slug,
    )
    snapshot.checkins_count += 1
    snapshot.streak_days = max(snapshot.streak_days, streak.current_streak_days)
    snapshot.score_pct = calculate_weekly_score(user, pillar_slug, week_start, snapshot.checkins_count)
    snapshot.save(update_fields=['checkins_count', 'streak_days', 'score_pct'])


@transaction.atomic
def apply_financial_transaction(tx: FinancialTransaction):
    local_dt = get_user_local_date(tx.user, tx.occurred_at)
    month_key = local_dt.strftime('%Y-%m')

    if tx.tx_type in {FinancialTransaction.TxType.EXPENSE, FinancialTransaction.TxType.BILL}:
        SpendingBudget.objects.filter(
            user=tx.user,
            category__iexact=tx.category,
            month_key=month_key,
        ).update(spent_ksh=F('spent_ksh') + tx.amount_ksh)

    record_checkin_activity(tx.user, pillar_slug='financial', occurred_at=tx.occurred_at)