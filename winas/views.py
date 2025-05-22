# performance_appraisal/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.db import models

from decimal import Decimal
from django.contrib.auth import authenticate, login # Import login for session auth if needed

from .models import (
    Department, Role, User, Pillar, KeyResultArea, PerformanceTarget,
    EmployeePerformance, SoftSkillRating, OverallAppraisal, Training,
    DevelopmentPlan, RatingKey
)
from .serializers import (
    DepartmentSerializer, RoleSerializer, UserSerializer, PillarSerializer,
    KeyResultAreaSerializer, PerformanceTargetSerializer, EmployeePerformanceSerializer,
    SoftSkillRatingSerializer, OverallAppraisalSerializer, TrainingSerializer,
    DevelopmentPlanSerializer, RatingKeySerializer, BonusCalculationSerializer,
    CEO_RegisterSerializer, LoginSerializer, SupervisorCreationSerializer,
    EmployeeCreationSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .permissions import IsAdminOrCEO, IsSupervisorOrAdmin, IsOwnerOrAdmin, IsCEO, IsDepartmentSupervisor


# --- Helper function to get tokens after authentication ---
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# --- Authentication & Registration Views ---

class CEO_RegisterView(APIView):
    permission_classes = [AllowAny] # Allow anyone to hit this endpoint initially

    def post(self, request):
        # Ensure only one CEO can self-register
        if User.objects.filter(is_superuser=True, role__role_name='CEO').exists():
            return Response(
                {"detail": "A CEO account already exists. Self-registration is not allowed."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CEO_RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        return Response({
            "message": "CEO account registered successfully. Please change your password if this is a temporary one.",
            "user": UserSerializer(user).data,
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Optionally log in the user for session-based authentication (e.g., for browsable API)
        # login(request, user)

        tokens = get_tokens_for_user(user)
        return Response({
            "message": "Login successful",
            "user": UserSerializer(user).data,
            "tokens": tokens
        }, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated] # User must be logged in to change password

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # --- Placeholder for actual email sending logic ---
        # In a real application, you would generate a unique token,
        # save it to the user record (or a temporary table), and
        # send an email to 'email' with a link containing the token.
        # Example:
        # from django.contrib.auth.tokens import default_token_generator
        # from django.utils.http import urlsafe_base64_encode
        # from django.utils.encoding import force_bytes
        # user = User.objects.get(email=email)
        # uid = urlsafe_base64_encode(force_bytes(user.pk))
        # token = default_token_generator.make_token(user)
        # reset_link = f"http://yourfrontend.com/reset-password/{uid}/{token}/"
        # send_mail_function("Password Reset", f"Click here to reset: {reset_link}", settings.DEFAULT_FROM_EMAIL, [email])
        # ---------------------------------------------------

        print(f"--- Password Reset Request (SIMULATED) ---")
        print(f"Password reset requested for: {email}")
        print(f"In a real app, an email with a reset link would be sent.")
        print(f"------------------------------------------")

        return Response(
            {"message": "If an account with that email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # This view would typically receive uid and token from the URL,
        # and new_password from the request body.
        # For simplicity, this example uses email directly for finding the user.
        # A full implementation requires Django's password reset views and tokens.
        serializer = PasswordResetConfirmSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.context['user_to_reset']
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# --- User Management Views (CEO & Supervisors) ---

class UserManagementListCreate(APIView):
    """
    Handles listing and creating users (supervisors by CEO, employees by supervisor).
    """
    permission_classes = [IsAuthenticated] # Base permission

    def get(self, request):
        # CEO can view all users
        if request.user.is_superuser and hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'CEO':
            users = User.objects.all().select_related('department', 'role')
        # Supervisors can only view users in their department
        elif hasattr(request.user, 'role') and request.user.role and \
             request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            users = User.objects.filter(department=request.user.department).select_related('department', 'role')
        else:
            # Other users (employees) can only view themselves
            users = User.objects.filter(pk=request.user.pk).select_related('department', 'role')

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # CEO creates Supervisors
        if request.user.is_superuser and hasattr(request.user, 'role') and request.user.role and request.user.role.role_name == 'CEO':
            serializer = SupervisorCreationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                "message": "Supervisor account created successfully. Temporary password printed to console.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        # Supervisors create Employees in their department
        elif hasattr(request.user, 'role') and request.user.role and \
             request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            serializer = EmployeeCreationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save(department=request.user.department) # Assign to supervisor's department
            employee_role, created = Role.objects.get_or_create(role_name='Employee')
            user.role = employee_role
            user.save()
            return Response({
                "message": "Employee account created successfully. Temporary password printed to console.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "You do not have permission to create users."},
                status=status.HTTP_403_FORBIDDEN
            )

class UserManagementDetail(APIView):
    """
    Handles retrieving, updating, and deleting specific users.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, request):
        obj = get_object_or_404(User.objects.select_related('department', 'role'), pk=pk)
        # Apply permission for viewing/managing this specific user
        if not (request.user.is_superuser or request.user.is_staff):
            # If not admin/CEO, check if it's their own profile
            if obj.pk == request.user.pk:
                return obj
            # If supervisor, check if user is in their department
            if hasattr(request.user, 'role') and request.user.role and \
               request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               request.user.department == obj.department:
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this user's data.")
        return obj

    def get(self, request, pk):
        user = self.get_object(pk, request)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk, request)
        # Only admin/CEO can change roles/departments. Supervisors can only update basic employee info.
        if not (request.user.is_superuser or request.user.is_staff):
            # Non-admin/CEO can only update their own profile
            if user.pk != request.user.pk:
                raise status.HTTP_403_FORBIDDEN("You can only update your own profile.")
            # Restrict fields they can update (e.g., cannot change department or role)
            restricted_fields = ['department', 'role', 'is_staff', 'is_superuser', 'is_active']
            for field in restricted_fields:
                if field in request.data:
                    return Response(
                        {"detail": f"You are not allowed to update the '{field}' field."},
                        status=status.HTTP_403_FORBIDDEN
                    )

        serializer = UserSerializer(user, data=request.data, partial=True) # Allow partial updates
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        user = self.get_object(pk, request)
        # Only CEO/Admin can delete users
        if not (request.user.is_superuser or request.user.is_staff):
            raise status.HTTP_403_FORBIDDEN("You do not have permission to delete users.")
        
        if user.pk == request.user.pk:
            return Response({"detail": "You cannot delete your own account via this endpoint."}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Generic APIView Mixins for CRUD (re-using from previous response) ---

class ListCreateAPIView(APIView):
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.all()
        if hasattr(self, 'get_queryset_filtered_by_user_or_department'):
            queryset = self.get_queryset_filtered_by_user_or_department(request, queryset)
        
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if hasattr(self, 'perform_create_with_user_or_department_context'):
            self.perform_create_with_user_or_department_context(serializer, request)
        else:
            serializer.save()
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyAPIView(APIView):
    queryset = None
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            obj = self.queryset.get(pk=pk)
            # Apply object-level permission check
            self.check_object_permissions(self.request, obj)
            return obj
        except self.queryset.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, *args, **kwargs):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if hasattr(self, 'perform_update_with_user_or_department_context'):
            self.perform_update_with_user_or_department_context(serializer, request)
        else:
            serializer.save()
            
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- APIViews for Each Model (Modified with Departmental Permissions) ---

class DepartmentListCreate(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrCEO] # CEO can add departments

class DepartmentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrCEO]

class RoleListCreate(ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrCEO] # CEO can manage roles

class RoleDetail(RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrCEO]

class PillarListCreate(ListCreateAPIView):
    queryset = Pillar.objects.all()
    serializer_class = PillarSerializer
    permission_classes = [IsSupervisorOrAdmin]

class PillarDetail(RetrieveUpdateDestroyAPIView):
    queryset = Pillar.objects.all()
    serializer_class = PillarSerializer
    permission_classes = [IsSupervisorOrAdmin]

class KeyResultAreaListCreate(ListCreateAPIView):
    queryset = KeyResultArea.objects.all().select_related('pillar')
    serializer_class = KeyResultAreaSerializer
    permission_classes = [IsSupervisorOrAdmin]

class KeyResultAreaDetail(RetrieveUpdateDestroyAPIView):
    queryset = KeyResultArea.objects.all().select_related('pillar')
    serializer_class = KeyResultAreaSerializer
    permission_classes = [IsSupervisorOrAdmin]

class PerformanceTargetListCreate(ListCreateAPIView):
    queryset = PerformanceTarget.objects.all().select_related('kra__pillar')
    serializer_class = PerformanceTargetSerializer
    permission_classes = [IsSupervisorOrAdmin]

class PerformanceTargetDetail(RetrieveUpdateDestroyAPIView):
    queryset = PerformanceTarget.objects.all().select_related('kra__pillar')
    serializer_class = PerformanceTargetSerializer
    permission_classes = [IsSupervisorOrAdmin]


class EmployeePerformanceListCreate(ListCreateAPIView):
    queryset = EmployeePerformance.objects.all().select_related('user', 'performance_target__kra__pillar')
    serializer_class = EmployeePerformanceSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin] # Supervisors can edit all, owners can view their own

    def get_queryset_filtered_by_user_or_department(self, request, queryset):
        if request.user.is_staff or request.user.is_superuser:
            return queryset.all()
        
        # Supervisors see performance of employees in their department
        if hasattr(request.user, 'role') and request.user.role and \
           request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            return queryset.filter(user__department=request.user.department)
        
        # Normal users see only their own performance
        return queryset.filter(user=request.user)

    def perform_create_with_user_or_department_context(self, serializer, request):
        # Ensure the user assigned to performance is in the supervisor's department
        if not (request.user.is_staff or request.user.is_superuser):
            target_user = serializer.validated_data.get('user')
            if not target_user or target_user.department != request.user.department:
                raise serializer.ValidationError("You can only create performance records for employees in your department.")
        serializer.save()


class EmployeePerformanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = EmployeePerformance.objects.all().select_related('user', 'performance_target__kra__pillar')
    serializer_class = EmployeePerformanceSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_object(self, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        # Apply IsOwnerOrAdmin or IsDepartmentSupervisor
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if obj.user == self.request.user: # Owner
                return obj
            if hasattr(self.request.user, 'role') and self.request.user.role and \
               self.request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               obj.user.department == self.request.user.department: # Department Supervisor
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this performance record.")
        return obj


class SoftSkillRatingListCreate(ListCreateAPIView):
    queryset = SoftSkillRating.objects.all().select_related('user', 'soft_skill_kra__pillar')
    serializer_class = SoftSkillRatingSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_queryset_filtered_by_user_or_department(self, request, queryset):
        if request.user.is_staff or request.user.is_superuser:
            return queryset.all()
        if hasattr(request.user, 'role') and request.user.role and \
           request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            return queryset.filter(user__department=request.user.department)
        return queryset.filter(user=request.user)

    def perform_create_with_user_or_department_context(self, serializer, request):
        if not (request.user.is_staff or request.user.is_superuser):
            target_user = serializer.validated_data.get('user')
            if not target_user or target_user.department != request.user.department:
                raise serializer.ValidationError("You can only create soft skill ratings for employees in your department.")
        serializer.save()

class SoftSkillRatingDetail(RetrieveUpdateDestroyAPIView):
    queryset = SoftSkillRating.objects.all().select_related('user', 'soft_skill_kra__pillar')
    serializer_class = SoftSkillRatingSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_object(self, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if obj.user == self.request.user:
                return obj
            if hasattr(self.request.user, 'role') and self.request.user.role and \
               self.request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               obj.user.department == self.request.user.department:
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this soft skill rating.")
        return obj


class OverallAppraisalListCreate(ListCreateAPIView):
    queryset = OverallAppraisal.objects.all().select_related('user', 'appraiser')
    serializer_class = OverallAppraisalSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_queryset_filtered_by_user_or_department(self, request, queryset):
        if request.user.is_staff or request.user.is_superuser:
            return queryset.all()
        if hasattr(request.user, 'role') and request.user.role and \
           request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            return queryset.filter(user__department=request.user.department)
        return queryset.filter(user=request.user)

    def perform_create_with_user_or_department_context(self, serializer, request):
        # Ensure the user being appraised is in the supervisor's department
        if not (request.user.is_staff or request.user.is_superuser):
            target_user = serializer.validated_data.get('user')
            if not target_user or target_user.department != request.user.department:
                raise serializer.ValidationError("You can only create appraisals for employees in your department.")
        serializer.save(appraiser=request.user) # Set the appraiser to the current user

class OverallAppraisalDetail(RetrieveUpdateDestroyAPIView):
    queryset = OverallAppraisal.objects.all().select_related('user', 'appraiser')
    serializer_class = OverallAppraisalSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_object(self, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if obj.user == self.request.user:
                return obj
            if hasattr(self.request.user, 'role') and self.request.user.role and \
               self.request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               obj.user.department == self.request.user.department:
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this appraisal.")
        return obj


class TrainingListCreate(ListCreateAPIView):
    queryset = Training.objects.all().select_related('user')
    serializer_class = TrainingSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_queryset_filtered_by_user_or_department(self, request, queryset):
        if request.user.is_staff or request.user.is_superuser:
            return queryset.all()
        if hasattr(request.user, 'role') and request.user.role and \
           request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            return queryset.filter(user__department=request.user.department)
        return queryset.filter(user=request.user)

    def perform_create_with_user_or_department_context(self, serializer, request):
        if not (request.user.is_staff or request.user.is_superuser):
            target_user = serializer.validated_data.get('user')
            if not target_user or target_user.department != request.user.department:
                raise serializer.ValidationError("You can only create training records for employees in your department.")
        serializer.save()

class TrainingDetail(RetrieveUpdateDestroyAPIView):
    queryset = Training.objects.all().select_related('user')
    serializer_class = TrainingSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_object(self, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if obj.user == self.request.user:
                return obj
            if hasattr(self.request.user, 'role') and self.request.user.role and \
               self.request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               obj.user.department == self.request.user.department:
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this training record.")
        return obj

class DevelopmentPlanListCreate(ListCreateAPIView):
    queryset = DevelopmentPlan.objects.all().select_related('user')
    serializer_class = DevelopmentPlanSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_queryset_filtered_by_user_or_department(self, request, queryset):
        if request.user.is_staff or request.user.is_superuser:
            return queryset.all()
        if hasattr(request.user, 'role') and request.user.role and \
           request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and request.user.department:
            return queryset.filter(user__department=request.user.department)
        return queryset.filter(user=request.user)

    def perform_create_with_user_or_department_context(self, serializer, request):
        if not (request.user.is_staff or request.user.is_superuser):
            target_user = serializer.validated_data.get('user')
            if not target_user or target_user.department != request.user.department:
                raise serializer.ValidationError("You can only create development plans for employees in your department.")
        serializer.save()

class DevelopmentPlanDetail(RetrieveUpdateDestroyAPIView):
    queryset = DevelopmentPlan.objects.all().select_related('user')
    serializer_class = DevelopmentPlanSerializer
    permission_classes = [IsSupervisorOrAdmin | IsOwnerOrAdmin]

    def get_object(self, pk):
        obj = get_object_or_404(self.queryset, pk=pk)
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if obj.user == self.request.user:
                return obj
            if hasattr(self.request.user, 'role') and self.request.user.role and \
               self.request.user.role.role_name in ['Supervisor', 'HOD-ICT', 'Ass.ICTM'] and \
               obj.user.department == self.request.user.department:
                return obj
            raise status.HTTP_403_FORBIDDEN("You do not have permission to access this development plan.")
        return obj

class RatingKeyListCreate(ListCreateAPIView):
    queryset = RatingKey.objects.all().order_by('point_scale_min')
    serializer_class = RatingKeySerializer
    permission_classes = [IsAdminUser]

class RatingKeyDetail(RetrieveUpdateDestroyAPIView):
    queryset = RatingKey.objects.all().order_by('point_scale_min')
    serializer_class = RatingKeySerializer
    permission_classes = [IsAdminUser]


# --- Bonus Calculation API View (CEO only) ---

class BonusCalculationAPIView(APIView):
    permission_classes = [IsAdminOrCEO]

    def post(self, request, *args, **kwargs):
        serializer = BonusCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        total_bonus_pool = serializer.validated_data['total_bonus_pool']
        period_under_review = serializer.validated_data['period_under_review']

        all_eligible_users = User.objects.filter(is_active=True)

        if not hasattr(User, 'annual_salary') or not isinstance(User._meta.get_field('annual_salary'), (models.DecimalField, models.FloatField)):
            return Response(
                {"error": "User model must have an 'annual_salary' DecimalField or FloatField for bonus calculation."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        sum_of_all_staff_annual_salary = all_eligible_users.aggregate(
            total_annual_salary=Sum('annual_salary')
        )['total_annual_salary']

        if not sum_of_all_staff_annual_salary or sum_of_all_staff_annual_salary == Decimal('0.00'):
            return Response(
                {"error": "Sum of all staff annual salaries is zero or not found. Cannot calculate bonus."},
                status=status.HTTP_400_BAD_REQUEST
            )

        bonus_results = []

        for user in all_eligible_users:
            # 1. Calculate Score for Strategic Objectives (Section B)
            employee_performances = EmployeePerformance.objects.filter(
                user=user,
                period_under_review=period_under_review,
                performance_target__kra__pillar__pillar_name__in=[
                    "SHARED PERFORMANCE AREAS", "ICT & BUSINESS PROCESSES"
                ]
            )
            total_strategic_weight = employee_performances.aggregate(sum_weight=Sum('performance_target__weight'))['sum_weight'] or Decimal('0.00')
            total_strategic_weighted_average = employee_performances.aggregate(sum_w_avg=Sum('weighted_average'))['sum_w_avg'] or Decimal('0.00')

            strategic_score = Decimal('0.00')
            if total_strategic_weight > Decimal('0.00'):
                strategic_score = (total_strategic_weighted_average / total_strategic_weight)

            # 2. Calculate Score for Soft Skills (Section C)
            soft_skill_ratings = SoftSkillRating.objects.filter(
                user=user,
                period_under_review=period_under_review,
                soft_skill_kra__pillar__pillar_name="SOFT SKILLS"
            )
            total_soft_skill_weight = soft_skill_ratings.aggregate(sum_weight=Sum('weight'))['sum_weight'] or Decimal('0.00')
            total_soft_skill_weighted_average = soft_skill_ratings.aggregate(sum_w_avg=Sum('weighted_average'))['sum_w_avg'] or Decimal('0.00')

            soft_skill_score = Decimal('0.00')
            if total_soft_skill_weight > Decimal('0.00'):
                soft_skill_score = (total_soft_skill_weighted_average / total_soft_skill_weight)

            strategic_percentage_contribution = Decimal('0.70') # 70%
            soft_skill_percentage_contribution = Decimal('0.30') # 30%

            score_at_strategic_percentage = strategic_score * strategic_percentage_contribution
            score_at_soft_skill_percentage = soft_skill_score * soft_skill_percentage_contribution

            total_employee_score = score_at_strategic_percentage + score_at_soft_skill_percentage
            
            performance_rating = total_employee_score

            employee_bonus = Decimal('0.00')
            warning_message = None

            if user.annual_salary is None:
                warning_message = f"User {user.username} has no annual salary defined, skipping bonus calculation for them."
            else:
                try:
                    employee_bonus = (user.annual_salary / sum_of_all_staff_annual_salary) * \
                                     (performance_rating * total_bonus_pool)
                except Exception as e:
                    warning_message = f"Error calculating bonus for {user.username}: {e}"
                    employee_bonus = Decimal('0.00')


            bonus_results.append({
                'user_id': user.id,
                'username': user.username,
                'employee_name': user.get_full_name(),
                'department': user.department.department_name if user.department else None,
                'role': user.role.role_name if user.role else None,
                'annual_salary': user.annual_salary,
                'strategic_score': round(strategic_score, 2),
                'soft_skill_score': round(soft_skill_score, 2),
                'total_employee_score': round(total_employee_score, 2),
                'performance_rating': round(performance_rating, 2),
                'calculated_bonus': round(employee_bonus, 2),
                'warnings': warning_message
            })

        return Response(bonus_results, status=status.HTTP_200_OK)