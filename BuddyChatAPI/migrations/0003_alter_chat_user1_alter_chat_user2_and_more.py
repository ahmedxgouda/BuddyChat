# Generated by Django 5.1.3 on 2024-12-01 19:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BuddyChatAPI', '0002_alter_customuser_bio_alter_customuser_profile_pic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1_chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chat',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2_chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='BuddyChatAPI.chat'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='BuddyChatAPI.message'),
        ),
        migrations.AlterField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
