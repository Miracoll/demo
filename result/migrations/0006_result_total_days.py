# Generated by Django 4.0.4 on 2023-11-19 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0005_result_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='total_days',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
