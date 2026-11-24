import uuid
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ==========================================
# SHARED ENUMS
# ==========================================
class PillarSlug(models.TextChoices):
    ACADEMICS = 'academics', 'Academics'
    EMOTIONAL = 'emotional', 'Emotional'
    SPIRITUAL = 'spiritual', 'Spiritual'
    MENTAL = 'mental', 'Mental'
    PHYSICAL = 'physical', 'Physical'
    FINANCIAL = 'financial', 'Financial'


# ==========================================
# 1. CORE, AUTH & PREFERENCES
# ==========================================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not full_name:
            raise ValueError('Full name is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        EMAIL = 'email', 'Email'
        GOOGLE = 'google', 'Google'
        APPLE = 'apple', 'Apple'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # AbstractBaseUser natively manages `password`
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )
    initials = models.CharField(max_length=10, blank=True)
    timezone = models.CharField(max_length=64, default='Africa/Nairobi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'


class UserPillarFocus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pillar_focuses')
    pillar_slug = models.CharField(max_length=32, choices=PillarSlug.choices)
    is_active = models.BooleanField(default=True)
    target_weight = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'user_pillar_focus'
        constraints = [
            models.UniqueConstraint(fields=['user', 'pillar_slug'], name='unique_user_pillar_focus'),
            models.CheckConstraint(
                check=Q(target_weight__lte=100),
                name='pillar_focus_weight_0_100',
            ),
        ]


class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_checkin_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'user_streaks'


# ==========================================
# 2. SHARED PROGRESS, HABITS & WEEKLY INSIGHTS
# ==========================================
class PillarGoal(models.Model):
    class Cadence(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        PAUSED = 'paused', 'Paused'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pillar_goals')
    pillar_slug = models.CharField(max_length=32, choices=PillarSlug.choices)
    subtab_slug = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=255)
    cadence = models.CharField(max_length=20, choices=Cadence.choices)
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pillar_goals'
        indexes = [
            models.Index(fields=['user', 'pillar_slug', 'status'], name='idx_goal_user_pillar_status'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(target_value__gt=0) & Q(current_value__gte=0),
                name='pillar_goal_non_negative_values',
            ),
        ]


class PillarCheckin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pillar_checkins')
    pillar_slug = models.CharField(max_length=32, choices=PillarSlug.choices)
    subtab_slug = models.CharField(max_length=64, blank=True)
    goal = models.ForeignKey(
        PillarGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkins',
    )
    title = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    metric_label = models.CharField(max_length=120, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pillar_checkins'
        indexes = [
            models.Index(fields=['user', 'pillar_slug', '-logged_at'], name='idx_checkin_user_pillar_date'),
        ]


class DailyHabit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_habits')
    pillar_slug = models.CharField(max_length=32, choices=PillarSlug.choices)
    title = models.CharField(max_length=255)
    scheduled_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'daily_habits'
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_habit_user_active'),
        ]


class HabitLog(models.Model):
    habit = models.ForeignKey(DailyHabit, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habit_logs')
    log_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'habit_logs'
        indexes = [
            models.Index(fields=['user', 'log_date'], name='idx_habitlog_user_date'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['habit', 'log_date'], name='unique_habit_log_per_day'),
        ]


class WeeklySnapshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_snapshots')
    week_start_date = models.DateField()
    pillar_slug = models.CharField(max_length=32, choices=PillarSlug.choices)
    score_pct = models.PositiveSmallIntegerField(default=0)
    checkins_count = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'weekly_snapshots'
        indexes = [
            models.Index(fields=['user', '-week_start_date'], name='idx_snapshot_user_week'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'week_start_date', 'pillar_slug'],
                name='unique_weekly_pillar_snapshot',
            ),
            models.CheckConstraint(
                check=Q(score_pct__lte=100),
                name='weekly_snapshot_score_0_100',
            ),
        ]


# ==========================================
# 3. ACADEMICS PILLAR
# ==========================================
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    credits = models.PositiveSmallIntegerField()
    current_grade_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    term = models.CharField(max_length=64)

    class Meta:
        db_table = 'courses'
        indexes = [
            models.Index(fields=['user', 'term'], name='idx_course_user_term'),
        ]


class Assignment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUBMITTED = 'submitted', 'Submitted'
        GRADED = 'graded', 'Graded'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    due_at = models.DateTimeField()
    weight_pct = models.DecimalField(max_digits=5, decimal_places=2)
    score_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = 'assignments'
        indexes = [
            models.Index(fields=['user', 'status', 'due_at'], name='idx_assign_user_status_due'),
        ]


class ReadingItem(models.Model):
    class Status(models.TextChoices):
        READING = 'reading', 'Reading'
        COMPLETED = 'completed', 'Completed'
        QUEUED = 'queued', 'Queued'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_items')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    total_pages = models.PositiveIntegerField()
    pages_read = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)

    class Meta:
        db_table = 'reading_items'
        constraints = [
            models.CheckConstraint(
                check=Q(pages_read__lte=models.F('total_pages')),
                name='reading_pages_read_lte_total',
            ),
        ]


class SkillTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_tracks')
    skill_name = models.CharField(max_length=120)
    proficiency_pct = models.PositiveSmallIntegerField(default=0)
    practice_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    last_practiced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'skill_tracks'
        constraints = [
            models.CheckConstraint(
                check=Q(proficiency_pct__lte=100),
                name='skill_proficiency_0_100',
            ),
        ]


class ExamPrepSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_prep_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exam_prep_sessions')
    topic = models.CharField(max_length=255)
    mock_score_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration_mins = models.PositiveIntegerField()
    session_date = models.DateField()

    class Meta:
        db_table = 'exam_prep_sessions'
        indexes = [
            models.Index(fields=['user', '-session_date'], name='idx_examprep_user_date'),
        ]


# ==========================================
# 4. EMOTIONAL PILLAR
# ==========================================
class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    prompt = models.TextField(blank=True)
    body = models.TextField()
    mood_label = models.CharField(max_length=64)
    mood_score = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journal_entries'
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_journal_user_created'),
        ]


class Relationship(models.Model):
    class Circle(models.TextChoices):
        FAMILY = 'family', 'Family'
        FRIENDS = 'friends', 'Friends'
        MENTOR = 'mentor', 'Mentor'
        COMMUNITY = 'community', 'Community'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relationships')
    person_name = models.CharField(max_length=120)
    circle = models.CharField(max_length=20, choices=Circle.choices)
    target_cadence_days = models.PositiveSmallIntegerField()
    last_connected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'relationships'


class Boundary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boundaries')
    title = models.CharField(max_length=255)
    context = models.TextField(blank=True)
    adherence_pct = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'boundaries'
        constraints = [
            models.CheckConstraint(
                check=Q(adherence_pct__lte=100),
                name='boundary_adherence_0_100',
            ),
        ]


class EmotionalTrigger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotional_triggers')
    trigger_name = models.CharField(max_length=255)
    pattern_note = models.TextField(blank=True)
    intensity = models.PositiveSmallIntegerField()
    coping_response = models.TextField(blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = 'emotional_triggers'
        indexes = [
            models.Index(fields=['user', '-occurred_at'], name='idx_trigger_user_occurred'),
        ]


# ==========================================
# 5. SPIRITUAL PILLAR
# ==========================================
class GratitudeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gratitude_entries')
    entry_text = models.TextField()
    category = models.CharField(max_length=64, blank=True)
    logged_date = models.DateField()

    class Meta:
        db_table = 'gratitude_entries'
        indexes = [
            models.Index(fields=['user', '-logged_date'], name='idx_gratitude_user_date'),
        ]


class CoreValue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_values')
    value_name = models.CharField(max_length=120)
    purpose_statement = models.TextField(blank=True)
    alignment_score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'core_values'
        constraints = [
            models.CheckConstraint(
                check=Q(alignment_score__lte=100),
                name='core_value_alignment_0_100',
            ),
        ]


class SacredReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sacred_readings')
    source_title = models.CharField(max_length=255)
    passage_ref = models.CharField(max_length=120)
    reflection = models.TextField(blank=True)
    read_at = models.DateTimeField()

    class Meta:
        db_table = 'sacred_readings'
        indexes = [
            models.Index(fields=['user', '-read_at'], name='idx_reading_user_read_at'),
        ]


class BreathSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='breath_sessions')
    pattern = models.CharField(max_length=64)  # e.g., 4-7-8
    duration_mins = models.PositiveIntegerField()
    completed_at = models.DateTimeField()

    class Meta:
        db_table = 'breath_sessions'
        indexes = [
            models.Index(fields=['user', '-completed_at'], name='idx_breath_user_completed'),
        ]


# ==========================================
# 6. MENTAL PILLAR
# ==========================================
class DigitalDetoxBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digital_detox_blocks')
    block_label = models.CharField(max_length=120)
    duration_mins = models.PositiveIntegerField()
    screen_time_saved_mins = models.PositiveIntegerField(default=0)
    logged_date = models.DateField()

    class Meta:
        db_table = 'digital_detox_blocks'
        indexes = [
            models.Index(fields=['user', '-logged_date'], name='idx_detox_user_date'),
        ]


class StressReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stress_resets')
    technique = models.CharField(max_length=120)
    stress_before = models.PositiveSmallIntegerField()
    stress_after = models.PositiveSmallIntegerField()
    duration_mins = models.PositiveIntegerField()
    logged_at = models.DateTimeField()

    class Meta:
        db_table = 'stress_resets'
        indexes = [
            models.Index(fields=['user', '-logged_at'], name='idx_stress_user_logged'),
        ]


class CognitiveNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cognitive_notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    tag = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cognitive_notes'
        indexes = [
            models.Index(fields=['user', '-updated_at'], name='idx_cognote_user_updated'),
        ]


class SleepWinddownLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_winddown_logs')
    screens_off_time = models.TimeField()
    routine_completed = models.BooleanField(default=False)
    log_date = models.DateField()

    class Meta:
        db_table = 'sleep_winddown_logs'
        constraints = [
            models.UniqueConstraint(fields=['user', 'log_date'], name='unique_user_winddown_per_day'),
        ]


# ==========================================
# 7. PHYSICAL PILLAR
# ==========================================
class SleepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_logs')
    bedtime = models.DateTimeField()
    wake_time = models.DateTimeField()
    duration_hrs = models.DecimalField(max_digits=4, decimal_places=2)
    recovery_score = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'sleep_logs'
        indexes = [
            models.Index(fields=['user', '-wake_time'], name='idx_sleeplog_user_wake'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(recovery_score__lte=100) & Q(duration_hrs__gte=0),
                name='sleep_log_valid_ranges',
            ),
        ]


class NutritionHydrationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_hydration_logs')
    log_date = models.DateField()
    water_liters = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    meals_on_plan = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'nutrition_hydration_logs'
        constraints = [
            models.UniqueConstraint(fields=['user', 'log_date'], name='unique_user_nutrition_per_day'),
            models.CheckConstraint(
                check=Q(water_liters__gte=0),
                name='nutrition_water_non_negative',
            ),
        ]


class EnergyCheckin(models.Model):
    class TimeOfDay(models.TextChoices):
        MORNING = 'morning', 'Morning'
        AFTERNOON = 'afternoon', 'Afternoon'
        EVENING = 'evening', 'Evening'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='energy_checkins')
    energy_level = models.PositiveSmallIntegerField()
    time_of_day = models.CharField(max_length=20, choices=TimeOfDay.choices)
    logged_at = models.DateTimeField()

    class Meta:
        db_table = 'energy_checkins'
        indexes = [
            models.Index(fields=['user', '-logged_at'], name='idx_energy_user_logged'),
        ]


class CardioStepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cardio_step_logs')
    activity_type = models.CharField(max_length=64)
    steps_count = models.PositiveIntegerField(default=0)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    duration_mins = models.PositiveIntegerField(default=0)
    logged_date = models.DateField()

    class Meta:
        db_table = 'cardio_step_logs'
        indexes = [
            models.Index(fields=['user', '-logged_date'], name='idx_cardio_user_date'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(distance_km__gte=0),
                name='cardio_distance_non_negative',
            ),
        ]


# ==========================================
# 8. FINANCIAL PILLAR (Ksh)
# ==========================================
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    bucket_name = models.CharField(max_length=120)
    target_amount_ksh = models.DecimalField(max_digits=14, decimal_places=2)
    current_amount_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monthly_autosave_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    apy_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'savings_goals'
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(target_amount_ksh__gt=0)
                    & Q(current_amount_ksh__gte=0)
                    & Q(monthly_autosave_ksh__gte=0)
                ),
                name='savings_goal_valid_amounts',
            ),
        ]


class Investment(models.Model):
    class AssetClass(models.TextChoices):
        EQUITY_INDEX = 'equity_index', 'Equity Index'
        BOND_ETF = 'bond_etf', 'Bond ETF'
        MONEY_MARKET = 'money_market', 'Money Market'
        RETIREMENT = 'retirement', 'Retirement'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    asset_name = models.CharField(max_length=120)
    asset_class = models.CharField(max_length=32, choices=AssetClass.choices)
    current_balance_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    target_allocation_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ytd_return_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        db_table = 'investments'
        constraints = [
            models.CheckConstraint(
                check=Q(current_balance_ksh__gte=0) & Q(target_allocation_pct__gte=0) & Q(target_allocation_pct__lte=100),
                name='investment_valid_balance_and_alloc',
            ),
        ]


class DebtAndBill(models.Model):
    class EntryType(models.TextChoices):
        DEBT = 'debt', 'Debt'
        FIXED_BILL = 'fixed_bill', 'Fixed Bill'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debts_and_bills')
    title = models.CharField(max_length=255)
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    principal_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    remaining_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monthly_payment_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    due_day = models.PositiveSmallIntegerField()
    autopay_enabled = models.BooleanField(default=False)

    class Meta:
        db_table = 'debts_and_bills'
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(due_day__gte=1)
                    & Q(due_day__lte=31)
                    & Q(principal_ksh__gte=0)
                    & Q(remaining_ksh__gte=0)
                    & Q(monthly_payment_ksh__gte=0)
                ),
                name='debt_bill_valid_amounts_and_day',
            ),
        ]


class SpendingBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spending_budgets')
    category = models.CharField(max_length=120)
    monthly_cap_ksh = models.DecimalField(max_digits=14, decimal_places=2)
    spent_ksh = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    month_key = models.CharField(max_length=7)  # e.g., "2026-11"

    class Meta:
        db_table = 'spending_budgets'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category', 'month_key'],
                name='unique_user_category_month_budget',
            ),
            models.CheckConstraint(
                check=Q(monthly_cap_ksh__gte=0) & Q(spent_ksh__gte=0),
                name='spending_budget_non_negative',
            ),
        ]


class FinancialTransaction(models.Model):
    class TxType(models.TextChoices):
        SAVING = 'saving', 'Saving'
        INVESTMENT = 'investment', 'Investment'
        BILL = 'bill', 'Bill'
        EXPENSE = 'expense', 'Expense'
        AVOIDED_IMPULSE = 'avoided_impulse', 'Avoided Impulse'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_transactions')
    tx_type = models.CharField(max_length=20, choices=TxType.choices)
    amount_ksh = models.DecimalField(max_digits=14, decimal_places=2)
    category = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = 'financial_transactions'
        indexes = [
            models.Index(fields=['user', '-occurred_at'], name='idx_fintx_user_occurred'),
            models.Index(fields=['user', 'tx_type', '-occurred_at'], name='idx_fintx_user_type_occurred'),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(amount_ksh__gt=0),
                name='financial_tx_positive_amount',
            ),
        ]