# Generated by Django 4.0.4 on 2022-12-23 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student', models.CharField(max_length=255)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('average', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5, null=True)),
                ('position', models.CharField(blank=True, max_length=3, null=True)),
                ('present', models.IntegerField(blank=True, null=True)),
                ('absent', models.IntegerField(blank=True, null=True)),
                ('term', models.IntegerField()),
                ('group', models.CharField(max_length=5)),
                ('arm', models.CharField(max_length=5)),
                ('year', models.CharField(blank=True, max_length=5, null=True)),
                ('session', models.CharField(blank=True, max_length=10, null=True)),
                ('principalcomment', models.TextField(blank=True, max_length=200, null=True)),
                ('gccomment', models.TextField(blank=True, max_length=200, null=True)),
                ('hostelcomment', models.TextField(blank=True, max_length=200, null=True)),
                ('teachercomment', models.TextField(blank=True, max_length=200, null=True)),
                ('approve', models.IntegerField(blank=True, default=0, null=True)),
                ('active', models.IntegerField(blank=True, default=1, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=200)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('owner', models.CharField(blank=True, max_length=20, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
