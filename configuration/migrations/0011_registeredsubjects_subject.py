# Generated by Django 4.0.4 on 2023-11-22 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0010_registeredsubjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredsubjects',
            name='subject',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
    ]
