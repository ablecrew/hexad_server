from api.common.mixins import UserOwnedSerializer
from api.models import (
    Assignment,
    Course,
    ExamPrepSession,
    ReadingItem,
    SkillTrack,
)


class CourseSerializer(UserOwnedSerializer):
    class Meta:
        model = Course
        fields = ['id', 'user', 'code', 'title', 'credits', 'current_grade_pct', 'term']


class AssignmentSerializer(UserOwnedSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'course', 'user', 'title', 'due_at', 'weight_pct', 'score_pct', 'status']

    def validate_course(self, course):
        return self._validate_user_owned_fk(course, 'Course')


class ReadingItemSerializer(UserOwnedSerializer):
    class Meta:
        model = ReadingItem
        fields = ['id', 'user', 'title', 'author', 'total_pages', 'pages_read', 'status']


class SkillTrackSerializer(UserOwnedSerializer):
    class Meta:
        model = SkillTrack
        fields = ['id', 'user', 'skill_name', 'proficiency_pct', 'practice_hours', 'last_practiced_at']


class ExamPrepSessionSerializer(UserOwnedSerializer):
    class Meta:
        model = ExamPrepSession
        fields = ['id', 'user', 'course', 'topic', 'mock_score_pct', 'duration_mins', 'session_date']

    def validate_course(self, course):
        return self._validate_user_owned_fk(course, 'Course')