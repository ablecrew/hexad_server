from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.core.views import WeeklySnapshotViewSet  # Adjust import if necessary

router = DefaultRouter()

router.register(
    r'core/weekly-snapshots',
    WeeklySnapshotViewSet,
    basename='weekly-snapshot'
)

urlpatterns = [
    path('auth/', include('api.auth_api.urls')),
    path('core/', include('api.core.urls')),
    path('academics/', include('api.academics.urls')),
    path('emotional/', include('api.emotional.urls')),
    path('spiritual/', include('api.spiritual.urls')),
    path('mental/', include('api.mental.urls')),
    path('physical/', include('api.physical.urls')),
    path('financial/', include('api.financial.urls')),
    path('', include(router.urls)),
]