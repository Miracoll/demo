# Generated by Django 4.0.4 on 2023-05-09 20:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applicant', '0010_alter_paid_applicant_approved_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paid_applicant',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
