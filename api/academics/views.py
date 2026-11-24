from django.db.models import Avg, Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.mixins import BaseUserScopedViewSet
from api.models import (
    Assignment,
    Course,
    ExamPrepSession,
    ReadingItem,
    SkillTrack,
)
from .serializers import (
    AssignmentSerializer,
    CourseSerializer,
    ExamPrepSessionSerializer,
    ReadingItemSerializer,
    SkillTrackSerializer,
)


class CourseViewSet(BaseUserScopedViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ['term']
    search_fields = ['code', 'title']


class AssignmentViewSet(BaseUserScopedViewSet):
    queryset = Assignment.objects.select_related('course')
    serializer_class = AssignmentSerializer
    filterset_fields = ['course', 'status']
    ordering = ['due_at']


class ReadingItemViewSet(BaseUserScopedViewSet):
    queryset = ReadingItem.objects.all()
    serializer_class = ReadingItemSerializer
    filterset_fields = ['status']
    search_fields = ['title', 'author']


class SkillTrackViewSet(BaseUserScopedViewSet):
    queryset = SkillTrack.objects.all()
    serializer_class = SkillTrackSerializer
    search_fields = ['skill_name']


class ExamPrepSessionViewSet(BaseUserScopedViewSet):
    queryset = ExamPrepSession.objects.select_related('course')
    serializer_class = ExamPrepSessionSerializer
    filterset_fields = ['course', 'session_date']
    ordering = ['-session_date']


class AcademicsSummaryView(APIView):
    """GET /api/academics/summary/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        avg_grade = Course.objects.filter(
            user=user, current_grade_pct__isnull=False
        ).aggregate(avg=Avg('current_grade_pct'))['avg']
        pending_assignments = Assignment.objects.filter(
            user=user, status=Assignment.Status.PENDING
        ).count()
        total_study_mins = ExamPrepSession.objects.filter(user=user).aggregate(
            total=Sum('duration_mins')
        )['total'] or 0
        total_practice_hrs = SkillTrack.objects.filter(user=user).aggregate(
            total=Sum('practice_hours')
        )['total'] or 0

        return Response({
            'average_grade_pct': round(avg_grade, 2) if avg_grade is not None else None,
            'pending_assignments_count': pending_assignments,
            'total_exam_prep_mins': total_study_mins,
            'total_skill_practice_hours': total_practice_hrs,
        })