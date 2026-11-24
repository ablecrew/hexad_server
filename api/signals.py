from decimal import Decimal
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.common.services import apply_financial_transaction, record_checkin_activity
from api.models import (
    CardioStepLog,
    FinancialTransaction,
    HabitLog,
    JournalEntry,
    PillarCheckin,
    PillarSlug,
    SleepLog,
)


def _schedule_activity(user, pillar_slug, goal=None, occurred_at=None, goal_increment=None):
    user_id = user.id
    goal_id = goal.id if goal else None
    transaction.on_commit(
        lambda: _run_activity(user_id, pillar_slug, goal_id, occurred_at, goal_increment)
    )


def _run_activity(user_id, pillar_slug, goal_id, occurred_at, goal_increment):
    from django.contrib.auth import get_user_model
    from api.models import PillarGoal

    User = get_user_model()
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return
    goal = PillarGoal.objects.filter(pk=goal_id).first() if goal_id else None
    record_checkin_activity(
        user=user,
        pillar_slug=pillar_slug,
        goal=goal,
        occurred_at=occurred_at,
        goal_increment=goal_increment,
    )


@receiver(post_save, sender=PillarCheckin)
def on_checkin_created(sender, instance: PillarCheckin, created: bool, **kwargs):
    if created and not kwargs.get('raw', False):
        _schedule_activity(
            user=instance.user,
            pillar_slug=instance.pillar_slug,
            goal=instance.goal,
            occurred_at=instance.logged_at,
            goal_increment=Decimal('1.00'),
        )


@receiver(post_save, sender=HabitLog)
def on_habit_log_saved(sender, instance: HabitLog, created: bool, **kwargs):
    if instance.completed and not kwargs.get('raw', False):
        _schedule_activity(
            user=instance.user,
            pillar_slug=instance.habit.pillar_slug,
            occurred_at=instance.completed_at,
        )


@receiver(post_save, sender=JournalEntry)
def on_journal_created(sender, instance: JournalEntry, created: bool, **kwargs):
    if created and not kwargs.get('raw', False):
        _schedule_activity(
            user=instance.user,
            pillar_slug=PillarSlug.EMOTIONAL,
            occurred_at=instance.created_at,
        )


@receiver(post_save, sender=SleepLog)
def on_sleep_log_created(sender, instance: SleepLog, created: bool, **kwargs):
    if created and not kwargs.get('raw', False):
        _schedule_activity(
            user=instance.user,
            pillar_slug=PillarSlug.PHYSICAL,
            occurred_at=instance.wake_time,
        )


@receiver(post_save, sender=CardioStepLog)
def on_cardio_log_created(sender, instance: CardioStepLog, created: bool, **kwargs):
    if created and not kwargs.get('raw', False):
        _schedule_activity(
            user=instance.user,
            pillar_slug=PillarSlug.PHYSICAL,
        )


@receiver(post_save, sender=FinancialTransaction)
def on_financial_transaction_created(sender, instance: FinancialTransaction, created: bool, **kwargs):
    if created and not kwargs.get('raw', False):
        tx_pk = instance.pk
        transaction.on_commit(lambda: _run_financial_tx(tx_pk))


def _run_financial_tx(tx_pk):
    tx = FinancialTransaction.objects.filter(pk=tx_pk).select_related('user').first()
    if tx:
        apply_financial_transaction(tx)