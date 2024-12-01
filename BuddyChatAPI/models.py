from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.svg')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date_joined',)
    
    
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, db_index=True)
    
    class Meta:
        ordering = ('date',)
        
class Chat(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user1_chats', db_index=True)
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user2_chats', db_index=True)
    archived = models.BooleanField(default=False, db_index=True)
    last_message = models.ForeignKey('ChatMessage', on_delete=models.SET_NULL, null=True, related_name='last_message')
    
    def __str__(self):
        return f'{self.user1} - {self.user2}'
    
    class Meta:
        ordering = ('-last_message__message__date',)

class ChatMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    
class UserGroup(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    members_count = models.IntegerField(default=0)
    archived = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_groups')
    group_image = models.ImageField(upload_to='group_images', default='group_images/default.svg')
    updated_at = models.DateTimeField(auto_now=True)
    last_message = models.ForeignKey('GroupMessage', on_delete=models.SET_NULL, null=True, related_name='last_message')
    class Meta:
        ordering = ('-last_message__message__date',)
    
class GroupMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='group_messages')
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='group_messages')
    
    class Meta:
        ordering = ('-message__date',)
    
class GroupMember(models.Model):
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_groups')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user_group', 'member')
        ordering = ('joined_at',)
        
class Notification(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-message__date',)
        
class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments')
    
    class Meta:
        ordering = ('-message__date',)
