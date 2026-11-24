from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'digital-detox-blocks', views.DigitalDetoxBlockViewSet, basename='digital-detox-block')
router.register(r'stress-resets', views.StressResetViewSet, basename='stress-reset')
router.register(r'cognitive-notes', views.CognitiveNoteViewSet, basename='cognitive-note')
router.register(r'sleep-winddown-logs', views.SleepWinddownLogViewSet, basename='sleep-winddown-log')

urlpatterns = [
    path('summary/', views.MentalSummaryView.as_view(), name='mental-summary'),
    path('', include(router.urls)),
]