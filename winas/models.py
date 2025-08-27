# performance_appraisal/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager # Or AbstractBaseUser if you need more control
from django.db.models.signals import post_save
from django.dispatch import receiver

# If you're extending Django's default User model, you might need to import it
# from django.conf import settings
# User = settings.AUTH_USER_MODEL # Use this if you have a custom User model set in settings.py


class Department(models.Model):
    """
    Stores information about each department.
    """
    # department_id is automatically created as 'id' by Django's AutoField
    department_name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Departments" # Correct plural for admin display

    def __str__(self):
        return self.department_name

class Role(models.Model):
    """
    Stores information about different roles within the organization.
    """
    # role_id is automatically created as 'id' by Django's AutoField
    role_name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.role_name

# Assuming you want to extend Django's built-in User model
# If you have a custom user model already defined, adjust accordingly.
class CustomUserManager(UserManager):
    """
    Custom manager for User model to allow login with email.
    """
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # If username is not provided, use the part before @ in email
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Superuser should be active

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
class User(AbstractUser): # Extending AbstractUser for authentication features
    """
    Custom User model to store employee details.
    Extends Django's AbstractUser for authentication features (username, password, email, etc.).
    """
    # user_id is inherited as 'id' from AbstractUser

    # Removed 'name' as AbstractUser often handles first_name/last_name.
    # If you need a single 'name' field, consider using `full_name` property or adding a CharField.
    # email is already part of AbstractUser
    # password is already part of AbstractUser
    email = models.EmailField(unique=True,max_length=255)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL, # If a department is deleted, users in it will have department set to NULL
        null=True,
        blank=True,
        related_name='users'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL, # If a role is deleted, users in it will have role set to NULL
        null=True,
        blank=True,
        related_name='users'
    )
    employee_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Corresponds to PF.NO in the appraisal tool."
    )
    annual_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Employee's annual salary for bonus calculation."
    )
     # Use the custom manager
    objects = CustomUserManager()

    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # No fields required when creating a user, as email is the username field

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return self.email # Or self.get_full_name() if you prefer


class Pillar(models.Model):
    """
    Defines the broad categories of performance (e.g., Shared Performance Areas, Soft Skills).
    """
    # pillar_id is automatically created as 'id' by Django's AutoField
    pillar_name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Pillars"

    def __str__(self):
        return self.pillar_name


class KeyResultArea(models.Model):
    """
    Defines specific key result areas (KRAs) under each pillar.
    """
    # kra_id is automatically created as 'id' by Django's AutoField
    pillar = models.ForeignKey(
        Pillar,
        on_delete=models.CASCADE, # Changed to CASCADE to allow pillar deletion to cascade to KRAs
        related_name='kras'
    )
    kra_name = models.CharField(max_length=255)
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Detailed description of the KRA, especially for soft skills."
    )

    class Meta:
        verbose_name = "Key Result Area"
        verbose_name_plural = "Key Result Areas"
        unique_together = ('pillar', 'kra_name') # Ensure KRA names are unique per pillar

    def __str__(self):
        return f"{self.kra_name} ({self.pillar.pillar_name})"


class PerformanceTarget(models.Model):
    """
    Defines the general targets for each Key Result Area.
    """
    # target_id is automatically created as 'id' by Django's AutoField
    kra = models.ForeignKey(
        KeyResultArea,
        on_delete=models.CASCADE, # Changed to CASCADE to allow KRA deletion to cascade to KPIs
        related_name='performance_targets'
    )
    target_description = models.TextField(
        help_text="The specific target description (e.g., 'Recruit 40 new members')."
    )
    target_value = models.IntegerField(
        null=True,
        blank=True,
        help_text="The numerical target figure (e.g., 40, 80000000)."
    )
    annual_target = models.IntegerField(
        null=True,
        blank=True,
        help_text="The annual target, which might differ from the primary target_value."
    )
    weight = models.IntegerField(
        help_text="The weight assigned to this target."
    )

    class Meta:
        verbose_name = "Performance Target"
        verbose_name_plural = "Performance Targets"

    def __str__(self):
        return f"Target for {self.kra.kra_name}: {self.target_description}"


class EmployeePerformance(models.Model):
    """
    Records an employee's actual performance against specific strategic targets for a given period.
    """
    # performance_id is automatically created as 'id' by Django's AutoField
    user = models.ForeignKey(
        'User', # Use string reference if User model is defined later or in another app
        on_delete=models.CASCADE, # If a user is deleted, their performance records are also deleted
        related_name='performance_records'
    )
    performance_target = models.ForeignKey(
        PerformanceTarget,
        on_delete=models.PROTECT, # Prevent deletion of target if performance records exist
        related_name='employee_performances'
    )
    # Using CharField for period for flexibility (e.g., "Jan-Jun 2024").
    # For more complex period tracking, consider a separate `AppraisalPeriod` model.
    period_under_review = models.CharField(max_length=100)
    actual_achievement = models.IntegerField(
        help_text="The actual value achieved by the employee."
    )
    # These can be properties or calculated on save if preferred,
    # but storing them can optimize reads for reporting.
    percentage_achieved = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calculated: Actual Achievement / Target Value."
    )
    actual_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="The rating given for the achievement (e.g., 60, 100)."
    )
    weighted_average = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calculated: Percentage Achieved * Weight."
    )
    comments = models.TextField(
        null=True,
        blank=True,
        help_text="Supervisor's comments on this specific performance area."
    )

    class Meta:
        verbose_name = "Employee Performance"
        verbose_name_plural = "Employee Performances"
        unique_together = ('user', 'performance_target', 'period_under_review')

    def __str__(self):
        return f"{self.user.username}'s performance for {self.performance_target.kra.kra_name} ({self.period_under_review})"

    def save(self, *args, **kwargs):
        # Calculate percentage_achieved and weighted_average before saving
        if self.performance_target.target_value is not None and self.performance_target.target_value != 0:
            self.percentage_achieved = (self.actual_achievement / self.performance_target.target_value)
        else:
            self.percentage_achieved = 0.0 # Handle division by zero

        self.weighted_average = self.percentage_achieved * self.performance_target.weight

        super().save(*args, **kwargs)


class SoftSkillRating(models.Model):
    """
    Specifically handles the soft skills ratings for an employee.
    """
    # rating_id is automatically created as 'id' by Django's AutoField
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='soft_skill_ratings'
    )
    # The KRA here should be specific to soft skills (e.g., Diligence, Teamwork)
    soft_skill_kra = models.ForeignKey(
        KeyResultArea,
        on_delete=models.PROTECT,
        related_name='soft_skill_ratings'
    )
    # Using CharField for period consistency with EmployeePerformance
    period_under_review = models.CharField(max_length=100, default="Annual") # Assuming soft skills are often annual
    rating = models.IntegerField(
        help_text="The score given for the soft skill (e.g., 80, 70)."
    )
    weight = models.IntegerField(
        help_text="The weight of the soft skill."
    )
    weighted_average = models.IntegerField(
        null=True,
        blank=True,
        help_text="Calculated: Rating * Weight (assuming rating is scaled, e.g., out of 100)."
    )
    comments = models.TextField(
        null=True,
        blank=True,
        help_text="Comments related to the soft skill rating."
    )

    class Meta:
        verbose_name = "Soft Skill Rating"
        verbose_name_plural = "Soft Skill Ratings"
        unique_together = ('user', 'soft_skill_kra', 'period_under_review')

    def __str__(self):
        return f"{self.user.username}'s {self.soft_skill_kra.kra_name} rating ({self.period_under_review})"

    def save(self, *args, **kwargs):
        # Assuming rating is on a scale that can be multiplied by weight directly or needs conversion
        self.weighted_average = (self.rating / 100.0) * self.weight if self.weight else 0.0 # Example if rating is %
        super().save(*args, **kwargs)


class OverallAppraisal(models.Model):
    """
    Stores the summarized appraisal results and final comments for a given period.
    """
    # appraisal_id is automatically created as 'id' by Django's AutoField
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE, # If appraisee user is deleted, their overall appraisal is also deleted
        related_name='overall_appraisal',
        help_text="The employee being appraised."
    )
    period_under_review = models.CharField(max_length=100)
    strategic_objectives_score = models.IntegerField(
        help_text="Total score for Strategic Objectives (e.g., Section B)."
    )
    soft_skills_score = models.IntegerField(
        help_text="Total score for Soft Skills (e.g., Section C)."
    )
    total_performance_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Combined score (Strategic Objectives + Soft Skills)."
    )
    final_comments_appraisee = models.TextField(null=True, blank=True)
    final_comments_appraiser = models.TextField(null=True, blank=True)
    final_comments_hod = models.TextField(null=True, blank=True)
    final_comments_hr = models.TextField(null=True, blank=True)
    final_comments_ceo = models.TextField(null=True, blank=True)
    date_of_appraisal = models.DateField()

    # The appraiser is also a User
    appraiser = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL, # If an appraiser is deleted, their appraisal records are not deleted, just set to NULL
        null=True,
        blank=True,
        related_name='appraisals_given',
        help_text="The supervisor who conducted the appraisal."
    )

    class Meta:
        verbose_name = "Overall Appraisal"
        verbose_name_plural = "Overall Appraisals"
        unique_together = ('user', 'period_under_review') # One overall appraisal per user per period

    def __str__(self):
        return f"Overall Appraisal for {self.user.username} ({self.period_under_review})"

    def save(self, *args, **kwargs):
        self.total_performance_rating = self.strategic_objectives_score + self.soft_skills_score
        super().save(*args, **kwargs)


class Training(models.Model):
    """
    Stores information about courses/workshops/training attended by an employee.
    """
    # training_id is automatically created as 'id' by Django's AutoField
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='trainings_attended'
    )
    course_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Trainings"

    def __str__(self):
        return f"{self.user.username} - {self.course_name}"


class DevelopmentPlan(models.Model):
    """
    Stores information about professional growth and development activities for an employee.
    """
    # plan_id is automatically created as 'id' by Django's AutoField
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='development_plans'
    )
    activity_description = models.TextField()
    manager_actions = models.TextField(
        null=True,
        blank=True,
        help_text="Manager's actions related to the development plan."
    )
    targeted_completion_date = models.DateField(null=True, blank=True)
    manager_signature_date = models.DateField(null=True, blank=True) # Date manager signed off on the plan

    class Meta:
        verbose_name = "Development Plan"
        verbose_name_plural = "Development Plans"

    def __str__(self):
        return f"Development Plan for {self.user.username}"


class RatingKey(models.Model):
    """
    Defines the general rating scale for performance.
    """
    # key_id is automatically created as 'id' by Django's AutoField
    point_scale_min = models.IntegerField()
    point_scale_max = models.IntegerField()
    description = models.CharField(max_length=255)
    associated_weight = models.IntegerField(
        null=True,
        blank=True,
        help_text="Weight associated with this rating key (e.g., for Soft Skills).")

    class Meta:
        verbose_name = "Rating Key"
        verbose_name_plural = "Rating Keys"
        ordering = ['point_scale_min'] # Order by scale for logical display

    def __str__(self):
        return f"{self.point_scale_min}% - {self.point_scale_max}%: {self.description}"