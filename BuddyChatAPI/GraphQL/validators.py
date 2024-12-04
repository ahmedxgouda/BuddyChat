from django.core.exceptions import ValidationError, PermissionDenied
from ..models import CustomUser, Chat
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from ..models import UserGroup

def validate_password(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if password.isalpha():
        raise ValidationError('Password must contain at least one digit')
    if password.isdigit():
        raise ValidationError('Password must contain at least one letter')
    if password.islower():
        raise ValidationError('Password must contain at least one uppercase letter')
    if password.isupper():
        raise ValidationError('Password must contain at least one lowercase letter')
    return True

def validate_user_data(username, email, password, phone, first_name, last_name):
    
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError(f'Username: {username} already exists')
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError(f'Email: {email} already exists')
    if CustomUser.objects.filter(phone=phone).exists():
        raise ValidationError(f'Phone number: {phone} already exists')
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError(f'Invalid email: {email}')
    
    if len(username) < 4:
        raise ValidationError('Username must be at least 4 characters long')
    if len(phone) != 13:
        raise ValidationError('Phone number must be 13 characters long')
    if len(first_name) < 2:
        raise ValidationError('First name must be at least 2 characters long')
    if len(last_name) < 2:
        raise ValidationError('Last name must be at least 2 characters long')
    validate_password(password)
    return True

def validate_message_content(content):
    if len(content) < 1:
        raise ValidationError('Message content cannot be empty')
    return True

def validate_chat_users(user1, user2):
    if Chat.objects.filter(user1=user1, user2=user2).exists() or Chat.objects.filter(user1=user2, user2=user1).exists():
        raise ValidationError('Chat already exists')
    return True
    
def validate_group_member(user_group, member):
    if user_group.members.filter(pk=member.pk).exists():
        raise ValidationError('User is already a member of this group')
    return True

def validate_group_message_sender(user_group, sender_id):
    if not user_group.members.filter(pk=sender_id).exists():
        raise ValidationError('User is not a member of this group')
    return True

def validate_chat_message(chat: Chat, sender_id):
    # Case 1: A user is trying to send a message to themselves
    # Case 2: A user is trying to send a message to a user who is not a member of the chat
    if chat.user1_id != sender_id and chat.user2_id != sender_id:
        raise ValidationError(f'A user is not a member of this chat')
    return True

def validate_group_title(title):
    if len(title) < 2:
        raise ValidationError('Group title must be at least 2 characters long')
    return True

def validate_admin(user_group, member, group_admin):
    if not user_group.members.filter(pk=group_admin.pk).exists():
        raise ValidationError('User is not a member of this group')
    if not group_admin.is_admin:
        raise PermissionDenied('User is not an admin of this group')
    return True
    