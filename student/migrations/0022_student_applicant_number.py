# Generated by Django 4.0.4 on 2024-11-02 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0021_student_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='applicant_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
