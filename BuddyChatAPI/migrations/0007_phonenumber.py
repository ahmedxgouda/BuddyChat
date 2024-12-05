# Generated by Django 5.1.3 on 2024-12-05 05:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuddyChatAPI', '0006_remove_message_receiver_alter_chat_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15)),
                ('country_code', models.CharField(max_length=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]