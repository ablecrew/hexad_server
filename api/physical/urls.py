from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sleep-logs', views.SleepLogViewSet, basename='sleep-log')
router.register(r'nutrition-hydration-logs', views.NutritionHydrationLogViewSet, basename='nutrition-hydration-log')
router.register(r'energy-checkins', views.EnergyCheckinViewSet, basename='energy-checkin')
router.register(r'cardio-step-logs', views.CardioStepLogViewSet, basename='cardio-step-log')

urlpatterns = [
    path('summary/', views.PhysicalSummaryView.as_view(), name='physical-summary'),
    path('', include(router.urls)),
]