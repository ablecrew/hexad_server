from django.db.models import Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    DebtAndBill,
    FinancialTransaction,
    Investment,
    SavingsGoal,
    SpendingBudget,
)
from .serializers import (
    DebtAndBillSerializer,
    FinancialTransactionSerializer,
    InvestmentSerializer,
    SavingsGoalSerializer,
    SpendingBudgetSerializer,
)


class SavingsGoalViewSet(BaseUserScopedViewSet):
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer


class InvestmentViewSet(BaseUserScopedViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer
    filterset_fields = ['asset_class']


class DebtAndBillViewSet(BaseUserScopedViewSet):
    queryset = DebtAndBill.objects.all()
    serializer_class = DebtAndBillSerializer
    filterset_fields = ['entry_type', 'autopay_enabled']


class SpendingBudgetViewSet(BaseUserScopedViewSet):
    queryset = SpendingBudget.objects.all()
    serializer_class = SpendingBudgetSerializer
    filterset_fields = ['category', 'month_key']


class FinancialTransactionViewSet(BaseUserScopedViewSet):
    queryset = FinancialTransaction.objects.all()
    serializer_class = FinancialTransactionSerializer
    filterset_fields = ['tx_type', 'category']
    ordering = ['-occurred_at']


class FinancialSummaryView(APIView):
    """GET /api/financial/summary/ — returns net savings, investments, and remaining debt in Ksh."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        total_savings = SavingsGoal.objects.filter(user=user).aggregate(
            total=Sum('current_amount_ksh')
        )['total'] or 0
        total_investments = Investment.objects.filter(user=user).aggregate(
            total=Sum('current_balance_ksh')
        )['total'] or 0
        total_debt = DebtAndBill.objects.filter(
            user=user, entry_type=DebtAndBill.EntryType.DEBT
        ).aggregate(total=Sum('remaining_ksh'))['total'] or 0

        return Response({
            'currency': 'Ksh',
            'total_savings_ksh': total_savings,
            'total_investments_ksh': total_investments,
            'total_debt_remaining_ksh': total_debt,
            'net_worth_ksh': total_savings + total_investments - total_debt,
        })