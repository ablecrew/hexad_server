from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'reading-items', views.ReadingItemViewSet, basename='reading-item')
router.register(r'skill-tracks', views.SkillTrackViewSet, basename='skill-track')
router.register(r'exam-prep-sessions', views.ExamPrepSessionViewSet, basename='exam-prep-session')

urlpatterns = [
    path('summary/', views.AcademicsSummaryView.as_view(), name='academics-summary'),
    path('', include(router.urls)),
]