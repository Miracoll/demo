# Generated by Django 4.0.4 on 2023-12-11 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0019_student_register_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paid_student',
            name='arm',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='paid_student',
            name='group',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
