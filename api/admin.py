from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    UserPillarFocus,
    UserStreak,
    PillarGoal,
    PillarCheckin,
    DailyHabit,
    HabitLog,
    WeeklySnapshot,
    Course,
    Assignment,
    ReadingItem,
    SkillTrack,
    ExamPrepSession,
    JournalEntry,
    Relationship,
    Boundary,
    EmotionalTrigger,
    GratitudeEntry,
    CoreValue,
    SacredReading,
    BreathSession,
    DigitalDetoxBlock,
    StressReset,
    CognitiveNote,
    SleepWinddownLog,
    SleepLog,
    NutritionHydrationLog,
    EnergyCheckin,
    CardioStepLog,
    SavingsGoal,
    Investment,
    DebtAndBill,
    SpendingBudget,
    FinancialTransaction,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'full_name', 'auth_provider', 'timezone', 'is_staff', 'is_active', 'created_at')
    list_filter = ('auth_provider', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'full_name', 'initials')
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'initials', 'auth_provider', 'timezone')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Timestamps', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
            },
        ),
    )


# 1. Core & Preferences
@admin.register(UserPillarFocus)
class UserPillarFocusAdmin(admin.ModelAdmin):
    list_display = ('user', 'pillar_slug', 'is_active', 'target_weight')
    list_filter = ('pillar_slug', 'is_active')
    search_fields = ('user__email', 'user__full_name')


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak_days', 'longest_streak_days', 'last_checkin_date')
    search_fields = ('user__email', 'user__full_name')


# 2. Shared Progress, Habits & Weekly Insights
@admin.register(PillarGoal)
class PillarGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'pillar_slug', 'cadence', 'current_value', 'target_value', 'unit', 'status', 'due_date')
    list_filter = ('pillar_slug', 'cadence', 'status')
    search_fields = ('title', 'user__email', 'subtab_slug')


@admin.register(PillarCheckin)
class PillarCheckinAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'pillar_slug', 'goal', 'metric_label', 'logged_at')
    list_filter = ('pillar_slug', 'logged_at')
    search_fields = ('title', 'note', 'user__email')
    autocomplete_fields = ('user', 'goal')
    date_hierarchy = 'logged_at'


@admin.register(DailyHabit)
class DailyHabitAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'pillar_slug', 'scheduled_time', 'is_active')
    list_filter = ('pillar_slug', 'is_active')
    search_fields = ('title', 'user__email')


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('habit', 'user', 'log_date', 'completed', 'completed_at')
    list_filter = ('completed', 'log_date')
    search_fields = ('habit__title', 'user__email')
    autocomplete_fields = ('user', 'habit')
    date_hierarchy = 'log_date'


@admin.register(WeeklySnapshot)
class WeeklySnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_start_date', 'pillar_slug', 'score_pct', 'checkins_count', 'streak_days')
    list_filter = ('pillar_slug', 'week_start_date')
    search_fields = ('user__email',)


# 3. Academics Pillar
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'user', 'term', 'credits', 'current_grade_pct')
    list_filter = ('term',)
    search_fields = ('code', 'title', 'user__email')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'user', 'status', 'weight_pct', 'score_pct', 'due_at')
    list_filter = ('status', 'due_at')
    search_fields = ('title', 'course__code', 'user__email')


@admin.register(ReadingItem)
class ReadingItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'user', 'pages_read', 'total_pages', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'author', 'user__email')


@admin.register(SkillTrack)
class SkillTrackAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'user', 'proficiency_pct', 'practice_hours', 'last_practiced_at')
    search_fields = ('skill_name', 'user__email')


@admin.register(ExamPrepSession)
class ExamPrepSessionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'course', 'user', 'duration_mins', 'mock_score_pct', 'session_date')
    list_filter = ('session_date',)
    search_fields = ('topic', 'course__code', 'user__email')


# 4. Emotional Pillar
@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('mood_label', 'mood_score', 'user', 'created_at')
    list_filter = ('mood_label', 'created_at')
    search_fields = ('body', 'prompt', 'user__email')
    autocomplete_fields = ('user',)
    date_hierarchy = 'created_at'


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('person_name', 'circle', 'user', 'target_cadence_days', 'last_connected_at')
    list_filter = ('circle',)
    search_fields = ('person_name', 'user__email')


@admin.register(Boundary)
class BoundaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'adherence_pct', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'context', 'user__email')


@admin.register(EmotionalTrigger)
class EmotionalTriggerAdmin(admin.ModelAdmin):
    list_display = ('trigger_name', 'intensity', 'user', 'occurred_at')
    list_filter = ('intensity', 'occurred_at')
    search_fields = ('trigger_name', 'pattern_note', 'coping_response', 'user__email')


# 5. Spiritual Pillar
@admin.register(GratitudeEntry)
class GratitudeEntryAdmin(admin.ModelAdmin):
    list_display = ('category', 'entry_text', 'user', 'logged_date')
    list_filter = ('category', 'logged_date')
    search_fields = ('entry_text', 'user__email')


@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ('value_name', 'alignment_score', 'user')
    search_fields = ('value_name', 'purpose_statement', 'user__email')


@admin.register(SacredReading)
class SacredReadingAdmin(admin.ModelAdmin):
    list_display = ('source_title', 'passage_ref', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('source_title', 'passage_ref', 'reflection', 'user__email')


@admin.register(BreathSession)
class BreathSessionAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'duration_mins', 'user', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('pattern', 'user__email')


# 6. Mental Pillar
@admin.register(DigitalDetoxBlock)
class DigitalDetoxBlockAdmin(admin.ModelAdmin):
    list_display = ('block_label', 'duration_mins', 'screen_time_saved_mins', 'user', 'logged_date')
    list_filter = ('logged_date',)
    search_fields = ('block_label', 'user__email')


@admin.register(StressReset)
class StressResetAdmin(admin.ModelAdmin):
    list_display = ('technique', 'stress_before', 'stress_after', 'duration_mins', 'user', 'logged_at')
    list_filter = ('logged_at',)
    search_fields = ('technique', 'user__email')


@admin.register(CognitiveNote)
class CognitiveNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'user', 'updated_at')
    list_filter = ('tag', 'updated_at')
    search_fields = ('title', 'content', 'user__email')


@admin.register(SleepWinddownLog)
class SleepWinddownLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_date', 'screens_off_time', 'routine_completed')
    list_filter = ('routine_completed', 'log_date')
    search_fields = ('user__email',)


# 7. Physical Pillar
@admin.register(SleepLog)
class SleepLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration_hrs', 'recovery_score', 'bedtime', 'wake_time')
    list_filter = ('wake_time',)
    search_fields = ('user__email',)
    autocomplete_fields = ('user',)
    date_hierarchy = 'wake_time'


@admin.register(NutritionHydrationLog)
class NutritionHydrationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_date', 'water_liters', 'meals_on_plan')
    list_filter = ('log_date',)
    search_fields = ('notes', 'user__email')


@admin.register(EnergyCheckin)
class EnergyCheckinAdmin(admin.ModelAdmin):
    list_display = ('user', 'time_of_day', 'energy_level', 'logged_at')
    list_filter = ('time_of_day', 'logged_at')
    search_fields = ('user__email',)


@admin.register(CardioStepLog)
class CardioStepLogAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'user', 'steps_count', 'distance_km', 'duration_mins', 'logged_date')
    list_filter = ('logged_date',)
    search_fields = ('activity_type', 'user__email')


# 8. Financial Pillar (Ksh)
@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('bucket_name', 'user', 'current_amount_ksh', 'target_amount_ksh', 'monthly_autosave_ksh', 'apy_pct')
    search_fields = ('bucket_name', 'user__email')


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('asset_name', 'asset_class', 'user', 'current_balance_ksh', 'target_allocation_pct', 'ytd_return_pct')
    list_filter = ('asset_class',)
    search_fields = ('asset_name', 'user__email')


@admin.register(DebtAndBill)
class DebtAndBillAdmin(admin.ModelAdmin):
    list_display = ('title', 'entry_type', 'user', 'remaining_ksh', 'monthly_payment_ksh', 'due_day', 'autopay_enabled')
    list_filter = ('entry_type', 'autopay_enabled')
    search_fields = ('title', 'user__email')


@admin.register(SpendingBudget)
class SpendingBudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'month_key', 'user', 'spent_ksh', 'monthly_cap_ksh')
    list_filter = ('month_key',)
    search_fields = ('category', 'user__email')


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_type', 'category', 'amount_ksh', 'user', 'occurred_at')
    list_filter = ('tx_type', 'occurred_at')
    search_fields = ('category', 'note', 'user__email')
    autocomplete_fields = ('user',)
    date_hierarchy = 'occurred_at'