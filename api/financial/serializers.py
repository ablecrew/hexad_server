from api.common.mixins import UserOwnedSerializer
from api.models import (
    DebtAndBill,
    FinancialTransaction,
    Investment,
    SavingsGoal,
    SpendingBudget,
)


class SavingsGoalSerializer(UserOwnedSerializer):
    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'user', 'bucket_name', 'target_amount_ksh',
            'current_amount_ksh', 'monthly_autosave_ksh', 'apy_pct',
        ]


class InvestmentSerializer(UserOwnedSerializer):
    class Meta:
        model = Investment
        fields = [
            'id', 'user', 'asset_name', 'asset_class',
            'current_balance_ksh', 'target_allocation_pct', 'ytd_return_pct',
        ]


class DebtAndBillSerializer(UserOwnedSerializer):
    class Meta:
        model = DebtAndBill
        fields = [
            'id', 'user', 'title', 'entry_type', 'principal_ksh',
            'remaining_ksh', 'monthly_payment_ksh', 'due_day', 'autopay_enabled',
        ]


class SpendingBudgetSerializer(UserOwnedSerializer):
    class Meta:
        model = SpendingBudget
        fields = ['id', 'user', 'category', 'monthly_cap_ksh', 'spent_ksh', 'month_key']


class FinancialTransactionSerializer(UserOwnedSerializer):
    class Meta:
        model = FinancialTransaction
        fields = ['id', 'user', 'tx_type', 'amount_ksh', 'category', 'note', 'occurred_at']