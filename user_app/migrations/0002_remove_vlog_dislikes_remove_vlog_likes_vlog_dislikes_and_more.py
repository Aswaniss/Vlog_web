# Generated by Django 5.1.3 on 2025-02-11 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vlog',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='vlog',
            name='likes',
        ),
        migrations.AddField(
            model_name='vlog',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='disliked_vlogs', to='user_app.register'),
        ),
        migrations.AddField(
            model_name='vlog',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_vlogs', to='user_app.register'),
        ),
    ]
