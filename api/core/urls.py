from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pillar-focuses', views.UserPillarFocusViewSet, basename='pillar-focus')
router.register(r'streaks', views.UserStreakViewSet, basename='streak')
router.register(r'goals', views.PillarGoalViewSet, basename='goal')
router.register(r'checkins', views.PillarCheckinViewSet, basename='checkin')
router.register(r'habits', views.DailyHabitViewSet, basename='habit')
router.register(r'habit-logs', views.HabitLogViewSet, basename='habit-log')
router.register(r'weekly-snapshots', views.WeeklySnapshotViewSet, basename='weekly-snapshot')

urlpatterns = [
    path('', include(router.urls)),
]