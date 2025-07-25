# Generated by Django 4.0.4 on 2023-10-28 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_remove_studentguardian_added_by_studentguardian_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='parent',
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_address',
            field=models.TextField(default='Soon', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_first_name',
            field=models.CharField(default='soon', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_last_name',
            field=models.CharField(default='soon', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='guardian_mobile',
            field=models.CharField(default='soon', max_length=15),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='StudentGuardian',
        ),
    ]
