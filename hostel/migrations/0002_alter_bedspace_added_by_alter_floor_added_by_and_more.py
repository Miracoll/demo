# Generated by Django 4.0.4 on 2022-12-23 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bedspace',
            name='added_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='floor',
            name='added_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='added_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='occupant',
            name='created_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='paid_occupant',
            name='added_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='room',
            name='added_by',
            field=models.CharField(max_length=100),
        ),
    ]
