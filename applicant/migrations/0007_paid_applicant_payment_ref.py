# Generated by Django 4.0.4 on 2023-02-11 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0006_rename_amount_paid_paid_applicant_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='paid_applicant',
            name='payment_ref',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
