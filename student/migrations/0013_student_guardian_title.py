# Generated by Django 4.0.4 on 2023-10-28 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_remove_student_parent_student_guardian_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='guardian_title',
            field=models.CharField(default='Mr', max_length=10),
            preserve_default=False,
        ),
    ]
