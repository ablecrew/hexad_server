from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'savings-goals', views.SavingsGoalViewSet, basename='savings-goal')
router.register(r'investments', views.InvestmentViewSet, basename='investment')
router.register(r'debts-and-bills', views.DebtAndBillViewSet, basename='debt-bill')
router.register(r'spending-budgets', views.SpendingBudgetViewSet, basename='spending-budget')
router.register(r'transactions', views.FinancialTransactionViewSet, basename='financial-transaction')

urlpatterns = [
    path('summary/', views.FinancialSummaryView.as_view(), name='financial-summary'),
    path('', include(router.urls)),
]