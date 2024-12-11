from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, null=True) # deprecated
    bio = models.TextField(max_length=500, blank=True, default='')
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.svg')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date_joined',)
    
class PhoneNumber(models.Model):
    number = models.CharField(max_length=15)
    country_code = models.CharField(max_length=5)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='phone_numbers')

    class Meta:
        unique_together = ('number', 'country_code')
        
    def __str__(self):
        return f'+{self.country_code} {self.number}'


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, db_index=True)
    
    class Meta:
        ordering = ('-date',)
        
    def __str__(self):
        return f'A message from {self.sender} at {self.date} - {self.content}'
        
class Chat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats', db_index=True)
    other_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='other_user_chats', db_index=True, null=True)
    archived = models.BooleanField(default=False, db_index=True)
    last_message = models.ForeignKey('ChatMessage', on_delete=models.SET_NULL, null=True, related_name='last_message')
    
    def __str__(self):
        return f'A chat with {self.user} - Last message: {self.last_message}, Archived: {self.archived}'
    class Meta:
        ordering = ('-last_message__message__date',)
    

class ChatMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='chat_messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages')
    
    def __str__(self):
        return f'{self.chat} - {self.message}'
    
class UserGroup(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(default='')
    members_count = models.IntegerField(default=0)
    archived = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_groups')
    group_image = models.ImageField(upload_to='group_images', default='group_images/default.svg')
    updated_at = models.DateTimeField(auto_now=True)
    last_message = models.ForeignKey('GroupMessage', on_delete=models.SET_NULL, null=True, related_name='last_message')
    class Meta:
        ordering = ('-last_message__message__date',)
        
    def __str__(self):
        return f'A group titled {self.title} created by {self.created_by} - Last message: {self.last_message}, Archived: {self.archived}'
        
class GroupMember(models.Model):
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_groups')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user_group', 'member')
        ordering = ('joined_at',)

class GroupMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='group_messages')
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='group_messages')
    group_member = models.ForeignKey(GroupMember, on_delete=models.CASCADE, related_name='group_messages')
    
    class Meta:
        ordering = ('-message__date',)
        
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
