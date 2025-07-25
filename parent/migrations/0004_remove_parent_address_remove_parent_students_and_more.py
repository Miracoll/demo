# Generated by Django 4.0.4 on 2023-10-28 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parent', '0003_rename_instangram_parent_instagram_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parent',
            name='address',
        ),
        migrations.RemoveField(
            model_name='parent',
            name='students',
        ),
        migrations.AddField(
            model_name='parent',
            name='current_student',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parent',
            name='added_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ParentStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='parent.parent')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='registered_student', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
