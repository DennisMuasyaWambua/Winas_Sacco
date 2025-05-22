# WINAS SACCO API Documentation

This document provides comprehensive information about all available API endpoints, including their required JSON payloads, authentication requirements, and calculation methodologies where applicable.

## Table of Contents

- [Authentication](#authentication)
- [User Management](#user-management)
- [Departments](#departments)
- [Roles](#roles)
- [Pillars](#pillars)
- [Key Result Areas](#key-result-areas)
- [Performance Targets](#performance-targets)
- [Employee Performance](#employee-performance)
- [Soft Skill Ratings](#soft-skill-ratings)
- [Overall Appraisals](#overall-appraisals)
- [Trainings](#trainings)
- [Development Plans](#development-plans)
- [Rating Keys](#rating-keys)
- [Bonus Calculation](#bonus-calculation)

## Authentication

### CEO Registration

Register the first CEO account in the system. This endpoint only works if no CEO exists.

- **URL**: `/register/ceo/`
- **Method**: `POST`
- **Authentication**: None required

**Request Payload**:
```json
{
  "email": "ceo@example.com",
  "password": "secure_password",
  "password2": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "employee_number": "CEO001",
  "annual_salary": 120000.00
}
```

**Response**:
```json
{
  "message": "CEO account registered successfully. Please change your password if this is a temporary one.",
  "user": {
    "id": 1,
    "email": "ceo@example.com",
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "employee_number": "CEO001",
    "annual_salary": 120000.00,
    "department": null,
    "department_name": null,
    "role": 1,
    "role_name": "CEO",
    "is_staff": true,
    "is_superuser": true,
    "is_active": true
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

### Login

Authenticate with email and password to receive access tokens.

- **URL**: `/login/`
- **Method**: `POST`
- **Authentication**: None required

**Request Payload**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response**:
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "employee_number": "EMP001",
    "annual_salary": 60000.00,
    "department": 1,
    "department_name": "Finance",
    "role": 2,
    "role_name": "Supervisor",
    "is_staff": true,
    "is_superuser": false,
    "is_active": true
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

### Change Password

Change the password for the authenticated user.

- **URL**: `/password/change/`
- **Method**: `POST`
- **Authentication**: JWT token required

**Request Payload**:
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password2": "new_secure_password"
}
```

**Response**:
```json
{
  "message": "Password changed successfully."
}
```

### Password Reset Request

Initiate a password reset process for a given email.

- **URL**: `/password/reset/request/`
- **Method**: `POST`
- **Authentication**: None required

**Request Payload**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```

### Password Reset Confirm

Complete the password reset process.

- **URL**: `/password/reset/confirm/`
- **Method**: `POST`
- **Authentication**: None required

**Request Payload**:
```json
{
  "email": "user@example.com",
  "new_password": "new_secure_password",
  "new_password2": "new_secure_password"
}
```

**Response**:
```json
{
  "message": "Password has been reset successfully."
}
```

## User Management

### List/Create Users

Get a list of users or create a new user.

- **URL**: `/users/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users (results filtered by role)
  - POST: CEO can create supervisors, supervisors can create employees

**Request Payload for CEO creating Supervisor**:
```json
{
  "email": "supervisor@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "employee_number": "SUP001",
  "annual_salary": 80000.00,
  "department": 1
}
```

**Request Payload for Supervisor creating Employee**:
```json
{
  "email": "employee@example.com",
  "first_name": "Robert",
  "last_name": "Johnson",
  "employee_number": "EMP001",
  "annual_salary": 50000.00
}
```

**Response**:
```json
{
  "message": "User account created successfully.",
  "user": {
    "id": 2,
    "email": "supervisor@example.com",
    "username": "jane.smith",
    "first_name": "Jane",
    "last_name": "Smith",
    "employee_number": "SUP001",
    "annual_salary": 80000.00,
    "department": 1,
    "department_name": "Finance",
    "role": 2,
    "role_name": "Supervisor",
    "is_staff": true,
    "is_superuser": false,
    "is_active": true
  }
}
```

### Retrieve/Update/Delete User

Manage a specific user by ID.

- **URL**: `/users/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Self or higher role
  - PUT: Self (limited fields) or higher role
  - DELETE: CEO/admin only

**Request Payload for PUT**:
```json
{
  "email": "updated.email@example.com",
  "username": "updated.username",
  "first_name": "UpdatedFirst",
  "last_name": "UpdatedLast",
  "employee_number": "EMP002",
  "annual_salary": 55000.00,
  "department": 2,
  "role": 3
}
```

**Response for GET/PUT**:
```json
{
  "id": 3,
  "email": "updated.email@example.com",
  "username": "updated.username",
  "first_name": "UpdatedFirst",
  "last_name": "UpdatedLast",
  "employee_number": "EMP002",
  "annual_salary": 55000.00,
  "department": 2,
  "department_name": "HR",
  "role": 3,
  "role_name": "Employee",
  "is_staff": false,
  "is_superuser": false,
  "is_active": true
}
```

## Departments

### List/Create Departments

Get a list of departments or create a new department.

- **URL**: `/departments/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: CEO/admin only

**Request Payload for POST**:
```json
{
  "department_name": "Marketing"
}
```

**Response**:
```json
{
  "id": 3,
  "department_name": "Marketing"
}
```

### Retrieve/Update/Delete Department

Manage a specific department by ID.

- **URL**: `/departments/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: CEO/admin only for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "department_name": "Digital Marketing"
}
```

**Response for GET/PUT**:
```json
{
  "id": 3,
  "department_name": "Digital Marketing"
}
```

## Roles

### List/Create Roles

Get a list of roles or create a new role.

- **URL**: `/roles/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: CEO/admin only

**Request Payload for POST**:
```json
{
  "role_name": "Team Lead"
}
```

**Response**:
```json
{
  "id": 4,
  "role_name": "Team Lead"
}
```

### Retrieve/Update/Delete Role

Manage a specific role by ID.

- **URL**: `/roles/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: CEO/admin only for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "role_name": "Senior Team Lead"
}
```

**Response for GET/PUT**:
```json
{
  "id": 4,
  "role_name": "Senior Team Lead"
}
```

## Pillars

### List/Create Pillars

Get a list of pillars or create a new pillar.

- **URL**: `/pillars/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "pillar_name": "Customer Service"
}
```

**Response**:
```json
{
  "id": 1,
  "pillar_name": "Customer Service"
}
```

### Retrieve/Update/Delete Pillar

Manage a specific pillar by ID.

- **URL**: `/pillars/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "pillar_name": "Customer Experience"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "pillar_name": "Customer Experience"
}
```

## Key Result Areas

### List/Create Key Result Areas

Get a list of KRAs or create a new KRA.

- **URL**: `/kras/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "pillar": 1,
  "kra_name": "Customer Satisfaction",
  "description": "Measures overall customer satisfaction levels"
}
```

**Response**:
```json
{
  "id": 1,
  "pillar": 1,
  "pillar_name": "Customer Experience",
  "kra_name": "Customer Satisfaction",
  "description": "Measures overall customer satisfaction levels"
}
```

### Retrieve/Update/Delete Key Result Area

Manage a specific KRA by ID.

- **URL**: `/kras/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "pillar": 1,
  "kra_name": "Customer Satisfaction Index",
  "description": "Measures the overall customer satisfaction through surveys"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "pillar": 1,
  "pillar_name": "Customer Experience",
  "kra_name": "Customer Satisfaction Index",
  "description": "Measures the overall customer satisfaction through surveys"
}
```

## Performance Targets

### List/Create Performance Targets

Get a list of performance targets or create a new target.

- **URL**: `/performance-targets/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "kra": 1,
  "target_description": "Achieve 90% customer satisfaction rating",
  "target_value": 90.0,
  "annual_target": 90.0,
  "weight": 25.0
}
```

**Response**:
```json
{
  "id": 1,
  "kra": 1,
  "kra_name": "Customer Satisfaction Index",
  "target_description": "Achieve 90% customer satisfaction rating",
  "target_value": 90.0,
  "annual_target": 90.0,
  "weight": 25.0
}
```

### Retrieve/Update/Delete Performance Target

Manage a specific performance target by ID.

- **URL**: `/performance-targets/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "kra": 1,
  "target_description": "Achieve 95% customer satisfaction rating",
  "target_value": 95.0,
  "annual_target": 95.0,
  "weight": 30.0
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "kra": 1,
  "kra_name": "Customer Satisfaction Index",
  "target_description": "Achieve 95% customer satisfaction rating",
  "target_value": 95.0,
  "annual_target": 95.0,
  "weight": 30.0
}
```

## Employee Performance

### List/Create Employee Performance Records

Get a list of employee performance records or create a new record.

- **URL**: `/employee-performance/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Filtered based on user role
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "user": 3,
  "performance_target": 1,
  "period_under_review": "2023 Q2",
  "actual_achievement": 88.5,
  "comments": "Good progress but still below target"
}
```

**Response**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "performance_target": 1,
  "target_description": "Achieve 95% customer satisfaction rating",
  "period_under_review": "2023 Q2",
  "actual_achievement": 88.5,
  "target_value": 95.0,
  "actual_rating": 4,
  "weighted_score": 26.55,
  "comments": "Good progress but still below target"
}
```

**Calculation Details**:
- `actual_rating`: Automatically calculated based on achievement percentage compared to target
- `weighted_score`: Calculated as `(actual_achievement / target_value) * weight`

### Retrieve/Update/Delete Employee Performance Record

Manage a specific performance record by ID.

- **URL**: `/employee-performance/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "actual_achievement": 92.0,
  "comments": "Significant improvement in customer satisfaction"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "performance_target": 1,
  "target_description": "Achieve 95% customer satisfaction rating",
  "period_under_review": "2023 Q2",
  "actual_achievement": 92.0,
  "target_value": 95.0,
  "actual_rating": 4,
  "weighted_score": 29.05,
  "comments": "Significant improvement in customer satisfaction"
}
```

## Soft Skill Ratings

### List/Create Soft Skill Ratings

Get a list of soft skill ratings or create a new rating.

- **URL**: `/soft-skill-ratings/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Filtered based on user role
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "user": 3,
  "soft_skill_kra": 2,
  "period_under_review": "2023 Q2",
  "rating": 4,
  "weight": 15.0,
  "comments": "Good communication skills"
}
```

**Response**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "soft_skill_kra": 2,
  "kra_name": "Communication",
  "period_under_review": "2023 Q2",
  "rating": 4,
  "weight": 15.0,
  "weighted_average": 12.0,
  "comments": "Good communication skills"
}
```

**Calculation Details**:
- `weighted_average`: Calculated as `(rating / 5) * weight`

### Retrieve/Update/Delete Soft Skill Rating

Manage a specific soft skill rating by ID.

- **URL**: `/soft-skill-ratings/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "rating": 5,
  "comments": "Excellent communication skills"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "soft_skill_kra": 2,
  "kra_name": "Communication",
  "period_under_review": "2023 Q2",
  "rating": 5,
  "weight": 15.0,
  "weighted_average": 15.0,
  "comments": "Excellent communication skills"
}
```

## Overall Appraisals

### List/Create Overall Appraisals

Get a list of overall appraisals or create a new appraisal.

- **URL**: `/overall-appraisals/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Filtered based on user role
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "user": 3,
  "period_under_review": "2023 Q2",
  "strategic_objectives_score": 85.5,
  "soft_skills_score": 90.0,
  "final_comments_appraisee": "I believe I've made good progress this quarter",
  "final_comments_appraiser": "Robert has shown consistent improvement",
  "date_of_appraisal": "2023-07-15"
}
```

**Response**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "period_under_review": "2023 Q2",
  "strategic_objectives_score": 85.5,
  "soft_skills_score": 90.0,
  "total_score": 86.85,
  "appraiser": 2,
  "appraiser_name": "Jane Smith",
  "final_comments_appraisee": "I believe I've made good progress this quarter",
  "final_comments_appraiser": "Robert has shown consistent improvement",
  "final_comments_hod": null,
  "final_comments_hr": null,
  "final_comments_ceo": null,
  "date_of_appraisal": "2023-07-15"
}
```

**Calculation Details**:
- `total_score`: Calculated as `(strategic_objectives_score * 0.7) + (soft_skills_score * 0.3)`
- `appraiser`: Automatically set to the current user creating the appraisal

### Retrieve/Update/Delete Overall Appraisal

Manage a specific overall appraisal by ID.

- **URL**: `/overall-appraisals/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Various levels based on user role

**Request Payload for PUT (by HOD)**:
```json
{
  "final_comments_hod": "I agree with the appraiser's assessment"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "period_under_review": "2023 Q2",
  "strategic_objectives_score": 85.5,
  "soft_skills_score": 90.0,
  "total_score": 86.85,
  "appraiser": 2,
  "appraiser_name": "Jane Smith",
  "final_comments_appraisee": "I believe I've made good progress this quarter",
  "final_comments_appraiser": "Robert has shown consistent improvement",
  "final_comments_hod": "I agree with the appraiser's assessment",
  "final_comments_hr": null,
  "final_comments_ceo": null,
  "date_of_appraisal": "2023-07-15"
}
```

## Trainings

### List/Create Trainings

Get a list of trainings or create a new training.

- **URL**: `/trainings/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Filtered based on user role
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "user": 3,
  "course_name": "Advanced Customer Service",
  "description": "Training on handling difficult customer situations",
  "completion_date": "2023-06-30",
  "comments": "Successfully completed"
}
```

**Response**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "course_name": "Advanced Customer Service",
  "description": "Training on handling difficult customer situations",
  "completion_date": "2023-06-30",
  "comments": "Successfully completed"
}
```

### Retrieve/Update/Delete Training

Manage a specific training by ID.

- **URL**: `/trainings/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "completion_date": "2023-07-05",
  "comments": "Successfully completed with distinction"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "course_name": "Advanced Customer Service",
  "description": "Training on handling difficult customer situations",
  "completion_date": "2023-07-05",
  "comments": "Successfully completed with distinction"
}
```

## Development Plans

### List/Create Development Plans

Get a list of development plans or create a new plan.

- **URL**: `/development-plans/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: Filtered based on user role
  - POST: Supervisors and CEO/admin

**Request Payload for POST**:
```json
{
  "user": 3,
  "activity_description": "Leadership skills development",
  "manager_actions": "Assign team project leadership",
  "targeted_completion_date": "2023-12-31",
  "manager_signature_date": "2023-08-01"
}
```

**Response**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "activity_description": "Leadership skills development",
  "manager_actions": "Assign team project leadership",
  "targeted_completion_date": "2023-12-31",
  "manager_signature_date": "2023-08-01"
}
```

### Retrieve/Update/Delete Development Plan

Manage a specific development plan by ID.

- **URL**: `/development-plans/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: Supervisors and CEO/admin for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "manager_actions": "Assign team project leadership and provide mentoring",
  "targeted_completion_date": "2024-03-31"
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "user": 3,
  "username": "robert.johnson",
  "employee_name": "Robert Johnson",
  "activity_description": "Leadership skills development",
  "manager_actions": "Assign team project leadership and provide mentoring",
  "targeted_completion_date": "2024-03-31",
  "manager_signature_date": "2023-08-01"
}
```

## Rating Keys

### List/Create Rating Keys

Get a list of rating keys or create a new rating key.

- **URL**: `/rating-keys/`
- **Method**: `GET` (list) or `POST` (create)
- **Authentication**: JWT token required
- **Permissions**: 
  - GET: All authenticated users
  - POST: CEO/admin only

**Request Payload for POST**:
```json
{
  "point_scale_min": 1,
  "point_scale_max": 2,
  "description": "Below Expectations",
  "associated_weight": 50
}
```

**Response**:
```json
{
  "id": 1,
  "point_scale_min": 1,
  "point_scale_max": 2,
  "description": "Below Expectations",
  "associated_weight": 50
}
```

### Retrieve/Update/Delete Rating Key

Manage a specific rating key by ID.

- **URL**: `/rating-keys/{id}/`
- **Method**: `GET` (retrieve), `PUT` (update), or `DELETE` (delete)
- **Authentication**: JWT token required
- **Permissions**: CEO/admin only for PUT and DELETE

**Request Payload for PUT**:
```json
{
  "description": "Significantly Below Expectations",
  "associated_weight": 40
}
```

**Response for GET/PUT**:
```json
{
  "id": 1,
  "point_scale_min": 1,
  "point_scale_max": 2,
  "description": "Significantly Below Expectations",
  "associated_weight": 40
}
```

## Bonus Calculation

### Calculate Bonus

Calculate employee bonuses based on performance metrics.

- **URL**: `/bonus-calculation/`
- **Method**: `POST`
- **Authentication**: JWT token required
- **Permissions**: CEO/admin only

**Request Payload**:
```json
{
  "total_bonus_pool": 100000.00,
  "period_under_review": "2023 Q2"
}
```

**Response**:
```json
[
  {
    "user_id": 2,
    "username": "jane.smith",
    "employee_name": "Jane Smith",
    "department": "Finance",
    "role": "Supervisor",
    "annual_salary": 80000.00,
    "strategic_score": 92.5,
    "soft_skill_score": 95.0,
    "total_employee_score": 93.25,
    "performance_rating": 0.31,
    "calculated_bonus": 31000.00,
    "warnings": null
  },
  {
    "user_id": 3,
    "username": "robert.johnson",
    "employee_name": "Robert Johnson",
    "department": "HR",
    "role": "Employee",
    "annual_salary": 55000.00,
    "strategic_score": 85.5,
    "soft_skills_score": 90.0,
    "total_employee_score": 86.85,
    "performance_rating": 0.2,
    "calculated_bonus": 20000.00,
    "warnings": null
  }
]
```

**Calculation Details**:
1. For each employee with performance records in the specified period:
   - Strategic objective score (70% weight): Aggregated from employee performance records
   - Soft skills score (30% weight): Aggregated from soft skill ratings
   - Total employee score = (strategic_score * 0.7) + (soft_skills_score * 0.3)

2. For all employees combined:
   - Calculate the total weighted score: Sum of (employee_score * annual_salary) for all employees
   - For each employee, calculate their bonus:
     - Performance rating = (employee_score * annual_salary) / total_weighted_score
     - Calculated bonus = total_bonus_pool * performance_rating

This methodology ensures that bonus allocation is proportional to both performance scores and annual salary, reflecting the employee's contribution to the organization.