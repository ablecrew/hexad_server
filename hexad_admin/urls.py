from django.urls import path
from .views import (
    AdminAnalyticsView,
    AdminInviteUserView,
    AdminOverviewView,
    AdminSettingsView,
    AdminUsersListView,
)

urlpatterns = [
    path("overview/", AdminOverviewView.as_view(), name="admin-overview"),
    path("users/", AdminUsersListView.as_view(), name="admin-users"),
    path("users/invite/", AdminInviteUserView.as_view(), name="admin-users-invite"),
    path("analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    path("settings/", AdminSettingsView.as_view(), name="admin-settings"),
]