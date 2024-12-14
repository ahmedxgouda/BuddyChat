# Generated by Django 5.1.4 on 2024-12-13 20:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuddyChatAPI', '0004_alter_chatmessage_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_groups', to=settings.AUTH_USER_MODEL),
        ),
    ]