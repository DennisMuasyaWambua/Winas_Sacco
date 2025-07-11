# Generated by Django 5.2.1 on 2025-06-10 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('winas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeperformance',
            name='actual_achievement',
            field=models.IntegerField(help_text='The actual value achieved by the employee.'),
        ),
        migrations.AlterField(
            model_name='employeeperformance',
            name='percentage_achieved',
            field=models.IntegerField(blank=True, help_text='Calculated: Actual Achievement / Target Value.', null=True),
        ),
        migrations.AlterField(
            model_name='employeeperformance',
            name='weighted_average',
            field=models.IntegerField(blank=True, help_text='Calculated: Percentage Achieved * Weight.', null=True),
        ),
        migrations.AlterField(
            model_name='overallappraisal',
            name='soft_skills_score',
            field=models.IntegerField(help_text='Total score for Soft Skills (e.g., Section C).'),
        ),
        migrations.AlterField(
            model_name='overallappraisal',
            name='strategic_objectives_score',
            field=models.IntegerField(help_text='Total score for Strategic Objectives (e.g., Section B).'),
        ),
        migrations.AlterField(
            model_name='overallappraisal',
            name='total_performance_rating',
            field=models.IntegerField(blank=True, help_text='Combined score (Strategic Objectives + Soft Skills).', null=True),
        ),
        migrations.AlterField(
            model_name='performancetarget',
            name='annual_target',
            field=models.IntegerField(blank=True, help_text='The annual target, which might differ from the primary target_value.', null=True),
        ),
        migrations.AlterField(
            model_name='performancetarget',
            name='target_value',
            field=models.IntegerField(blank=True, help_text='The numerical target figure (e.g., 40, 80000000).', null=True),
        ),
        migrations.AlterField(
            model_name='performancetarget',
            name='weight',
            field=models.IntegerField(help_text='The weight assigned to this target.'),
        ),
        migrations.AlterField(
            model_name='softskillrating',
            name='weight',
            field=models.IntegerField(help_text='The weight of the soft skill.'),
        ),
        migrations.AlterField(
            model_name='softskillrating',
            name='weighted_average',
            field=models.IntegerField(blank=True, help_text='Calculated: Rating * Weight (assuming rating is scaled, e.g., out of 100).', null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='annual_salary',
            field=models.IntegerField(blank=True, help_text="Employee's annual salary for bonus calculation.", null=True),
        ),
    ]
