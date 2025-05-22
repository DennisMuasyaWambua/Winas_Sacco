# performance_appraisal/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.crypto import get_random_string
from django.conf import settings

from .models import (
    Department, Role, User, Pillar, KeyResultArea, PerformanceTarget,
    EmployeePerformance, SoftSkillRating, OverallAppraisal, Training,
    DevelopmentPlan, RatingKey
)

# --- Existing Serializers (No major changes, just ensure they use 'email' for user-related fields if needed) ---

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'employee_number', 'annual_salary', 'department', 'department_name', 'role', 'role_name', 'is_staff', 'is_superuser', 'is_active']
        read_only_fields = ['is_staff', 'is_superuser', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False} # Password not always required in update
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

# ... (other existing serializers like PillarSerializer, KeyResultAreaSerializer, etc. remain largely the same) ...
# Ensure they correctly handle user foreign keys.

class PillarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pillar
        fields = '__all__'

class KeyResultAreaSerializer(serializers.ModelSerializer):
    pillar_name = serializers.CharField(source='pillar.pillar_name', read_only=True)

    class Meta:
        model = KeyResultArea
        fields = '__all__'

class PerformanceTargetSerializer(serializers.ModelSerializer):
    kra_name = serializers.CharField(source='kra.kra_name', read_only=True)
    pillar_name = serializers.CharField(source='kra.pillar.pillar_name', read_only=True)

    class Meta:
        model = PerformanceTarget
        fields = '__all__'

class EmployeePerformanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    kra_name = serializers.CharField(source='performance_target.kra.kra_name', read_only=True)
    target_description = serializers.CharField(source='performance_target.target_description', read_only=True)
    target_value = serializers.DecimalField(source='performance_target.target_value', max_digits=15, decimal_places=2, read_only=True)
    weight = serializers.DecimalField(source='performance_target.weight', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = EmployeePerformance
        fields = '__all__'
        read_only_fields = ['percentage_achieved', 'weighted_average']

class SoftSkillRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    soft_skill_kra_name = serializers.CharField(source='soft_skill_kra.kra_name', read_only=True)

    class Meta:
        model = SoftSkillRating
        fields = '__all__'
        read_only_fields = ['weighted_average']

class OverallAppraisalSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    appraiser_name = serializers.CharField(source='appraiser.get_full_name', read_only=True)

    class Meta:
        model = OverallAppraisal
        fields = '__all__'
        read_only_fields = ['total_performance_rating']

class TrainingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Training
        fields = '__all__'

class DevelopmentPlanSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = DevelopmentPlan
        fields = '__all__'

class RatingKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingKey
        fields = '__all__'


# --- New Serializers for Auth and User Management ---

class CEO_RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'employee_number', 'annual_salary']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            employee_number=validated_data.get('employee_number'),
            annual_salary=validated_data.get('annual_salary'),
            is_staff=True, # CEO is staff
            is_superuser=True, # CEO is superuser for self-registration
            is_active=True
        )
        # Assign CEO role if it exists
        ceo_role, created = Role.objects.get_or_create(role_name='CEO')
        user.role = ceo_role
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is inactive.")
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

class SupervisorCreationSerializer(serializers.ModelSerializer):
    # Password will be auto-generated
    password = serializers.CharField(write_only=True, required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'employee_number', 'annual_salary', 'department', 'password']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'employee_number': {'required': True},
            'annual_salary': {'required': True},
        }

    def create(self, validated_data):
        # Generate a temporary password
        temp_password = get_random_string(length=12)
        validated_data['password'] = temp_password # Store for sending to supervisor

        user = User.objects.create_user(
            email=validated_data['email'],
            password=temp_password,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            employee_number=validated_data.get('employee_number'),
            annual_salary=validated_data.get('annual_salary'),
            department=validated_data.get('department'),
            is_staff=True, # Supervisors are staff
            is_active=True # Active by default
        )
        supervisor_role, created = Role.objects.get_or_create(role_name='Supervisor')
        user.role = supervisor_role
        user.save()

        # In a real application, you would send an email with temp_password to validated_data['email']
        print(f"--- Supervisor Account Created ---")
        print(f"Email: {user.email}")
        print(f"Temporary Password: {temp_password}")
        print(f"Please instruct supervisor to reset password upon first login.")
        print(f"----------------------------------")

        return user

class EmployeeCreationSerializer(serializers.ModelSerializer):
    # Password will be auto-generated
    password = serializers.CharField(write_only=True, required=False)
    # Department will be implicitly set by the supervisor's department

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'employee_number', 'annual_salary', 'password']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'employee_number': {'required': True},
            'annual_salary': {'required': True},
        }

    def create(self, validated_data):
        # Generate a temporary password
        temp_password = get_random_string(length=12)
        validated_data['password'] = temp_password # Store for sending to employee

        # The department and role will be set in the view based on the requesting supervisor
        user = User.objects.create_user(
            email=validated_data['email'],
            password=temp_password,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            employee_number=validated_data.get('employee_number'),
            annual_salary=validated_data.get('annual_salary'),
            is_active=True # Active by default
        )
        employee_role, created = Role.objects.get_or_create(role_name='Employee')
        user.role = employee_role
        user.save()

        # In a real application, you would send an email with temp_password to validated_data['email']
        print(f"--- Employee Account Created ---")
        print(f"Email: {user.email}")
        print(f"Temporary Password: {temp_password}")
        print(f"Please instruct employee to reset password upon first login.")
        print(f"----------------------------------")

        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password was entered incorrectly. Please try again.")
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    # In a real app, this would trigger an email with a reset link/token
    # For this example, we'll just acknowledge the request.
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    # This serializer would typically receive a UID and token from a reset link
    # For simplicity, we'll assume a direct password change for a known user for now
    # A full implementation requires Django's password reset views and tokens.
    # This is a placeholder for the concept.
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return data

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            self.context['user_to_reset'] = user # Store user for later use in view
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

# Serializer for Bonus Calculation (no changes)
class BonusCalculationSerializer(serializers.Serializer):
    total_bonus_pool = serializers.DecimalField(max_digits=15, decimal_places=2, help_text="Total bonus amount available for distribution.")
    period_under_review = serializers.CharField(max_length=100, help_text="The appraisal period for which bonus is being calculated.")