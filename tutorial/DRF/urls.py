from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenVerifyView
from .views import *
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


router = DefaultRouter()
router.register('register', registerUserViewSet, basename='register')
router.register('TaskViewSet', TaskViewSet, basename='createTask')
router.register('users', UsersViewSet, basename='userList')



urlpatterns = [
    path('api/', include(router.urls)),
    
    path('tasks/<int:pk>/logs/', TaskAuditLogView.as_view(), name='task-logs'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/tasks/metrics/', TaskMetricsView.as_view(), name='task-metrics'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/task/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}), name='task-detail'),
    path('api/tasks/export_csv/', ExportTaskCSVView.as_view(), name='import-tasks-csv'),
    path('api/tasks/import_csv/', ImportTaskCSVView.as_view(), name='export-tasks-csv'),
    ]
"""    path('api/task/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}), name='task-detail'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),"""