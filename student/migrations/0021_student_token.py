# Generated by Django 4.0.4 on 2024-11-02 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0020_alter_paid_student_arm_alter_paid_student_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='token',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
