# Generated by Django 4.0.4 on 2023-11-15 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0015_alter_student_arm'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='day',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='month',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
