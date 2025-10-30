# performance_appraisal/urls.py
from django.urls import path
from .views import (
    DepartmentListCreate, DepartmentDetail,
    RoleListCreate, RoleDetail,
    UserManagementListCreate, UserManagementDetail, # Changed from UserListCreate, UserDetail
    MetricsListCreate, MetricsDetail,
    PillarListCreate, PillarDetail,
    KeyResultAreaListCreate, KeyResultAreaDetail,
    PerformanceTargetListCreate, PerformanceTargetDetail,
    EmployeePerformanceListCreate, EmployeePerformanceDetail,
    SoftSkillRatingListCreate, SoftSkillRatingDetail,
    OverallAppraisalListCreate, OverallAppraisalDetail,
    TrainingListCreate, TrainingDetail,
    DevelopmentPlanListCreate, DevelopmentPlanDetail,
    RatingKeyListCreate, RatingKeyDetail,
    BonusCalculationAPIView,
    CEO_RegisterView, LoginView, PasswordChangeView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    # Authentication & Registration
    path('register/ceo/', CEO_RegisterView.as_view(), name='ceo-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # User Management (CEO & Supervisors)
    path('users/', UserManagementListCreate.as_view(), name='user-management-list-create'),
    path('users/<int:pk>/', UserManagementDetail.as_view(), name='user-management-detail'),

    # Core Data Management (Departments, Roles, etc.)
    path('departments/', DepartmentListCreate.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentDetail.as_view(), name='department-detail'),

    path('roles/', RoleListCreate.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetail.as_view(), name='role-detail'),

    path('metrics/', MetricsListCreate.as_view(), name='metrics-list-create'),
    path('metrics/<int:pk>/', MetricsDetail.as_view(), name='metrics-detail'),

    path('pillars/', PillarListCreate.as_view(), name='pillar-list-create'),
    path('pillars/<int:pk>/', PillarDetail.as_view(), name='pillar-detail'),

    path('kras/', KeyResultAreaListCreate.as_view(), name='kra-list-create'),
    path('kras/<int:pk>/', KeyResultAreaDetail.as_view(), name='kra-detail'),

    path('performance-targets/', PerformanceTargetListCreate.as_view(), name='performance-target-list-create'),
    path('performance-targets/<int:pk>/', PerformanceTargetDetail.as_view(), name='performance-target-detail'),

    path('employee-performance/', EmployeePerformanceListCreate.as_view(), name='employee-performance-list-create'),
    path('employee-performance/<int:pk>/', EmployeePerformanceDetail.as_view(), name='employee-performance-detail'),

    path('soft-skill-ratings/', SoftSkillRatingListCreate.as_view(), name='soft-skill-rating-list-create'),
    path('soft-skill-ratings/<int:pk>/', SoftSkillRatingDetail.as_view(), name='soft-skill-rating-detail'),

    path('overall-appraisals/', OverallAppraisalListCreate.as_view(), name='overall-appraisal-list-create'),
    path('overall-appraisals/<int:pk>/', OverallAppraisalDetail.as_view(), name='overall-appraisal-detail'),

    path('trainings/', TrainingListCreate.as_view(), name='training-list-create'),
    path('trainings/<int:pk>/', TrainingDetail.as_view(), name='training-detail'),

    path('development-plans/', DevelopmentPlanListCreate.as_view(), name='development-plan-list-create'),
    path('development-plans/<int:pk>/', DevelopmentPlanDetail.as_view(), name='development-plan-detail'),

    path('rating-keys/', RatingKeyListCreate.as_view(), name='rating-key-list-create'),
    path('rating-keys/<int:pk>/', RatingKeyDetail.as_view(), name='rating-key-detail'),

    # Bonus Calculation
    path('bonus-calculation/', BonusCalculationAPIView.as_view(), name='bonus-calculation'),
]