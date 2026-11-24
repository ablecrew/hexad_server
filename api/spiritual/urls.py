from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'gratitude-entries', views.GratitudeEntryViewSet, basename='gratitude-entry')
router.register(r'core-values', views.CoreValueViewSet, basename='core-value')
router.register(r'sacred-readings', views.SacredReadingViewSet, basename='sacred-reading')
router.register(r'breath-sessions', views.BreathSessionViewSet, basename='breath-session')

urlpatterns = [
    path('summary/', views.SpiritualSummaryView.as_view(), name='spiritual-summary'),
    path('', include(router.urls)),
]