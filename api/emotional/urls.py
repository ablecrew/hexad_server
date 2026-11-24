from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'journal-entries', views.JournalEntryViewSet, basename='journal-entry')
router.register(r'relationships', views.RelationshipViewSet, basename='relationship')
router.register(r'boundaries', views.BoundaryViewSet, basename='boundary')
router.register(r'triggers', views.EmotionalTriggerViewSet, basename='emotional-trigger')

urlpatterns = [
    path('summary/', views.EmotionalSummaryView.as_view(), name='emotional-summary'),
    path('', include(router.urls)),
]