# Generated by Django 5.0.3 on 2024-04-03 08:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('what_to_do_app', '0005_rename_user_activity_useractivityemotion_activity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='user_emotions',
        ),
        migrations.RemoveField(
            model_name='useractivityemotion',
            name='activity',
        ),
        migrations.AddField(
            model_name='activityevent',
            name='user_emotions',
            field=models.ManyToManyField(related_name='emotions', through='what_to_do_app.UserActivityEmotion', to='what_to_do_app.emotion'),
        ),
        migrations.AddField(
            model_name='useractivityemotion',
            name='activityevent',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='what_to_do_app.activityevent'),
            preserve_default=False,
        ),
    ]
