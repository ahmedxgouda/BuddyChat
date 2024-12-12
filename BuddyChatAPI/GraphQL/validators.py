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
    if len(phone) < 8 or len(phone) > 15:
        raise ValidationError('Phone number must be between 8 and 15 characters long')
    if len(first_name) < 2:
        raise ValidationError('First name must be at least 2 characters long')
    if len(last_name) < 2:
        raise ValidationError('Last name must be at least 2 characters long')
    validate_password(password)
    return True

def validate_phone_number(phone, country_code=None):
    if len(phone) < 8 or len(phone) > 15:
        raise ValidationError('Phone number must be between 8 and 15 characters long')
    if not phone.isdigit():
        raise ValidationError('Phone number must contain only digits')
    if country_code and not country_code.isdigit():
        raise ValidationError('Country code must contain only digits')
    return True

def validate_message_content(content):
    if len(content) < 1:
        raise ValidationError('Message content cannot be empty')
    return True

    
def validate_group_member(user_group, member):
    if user_group.members.filter(pk=member.pk).exists():
        raise ValidationError('User is already a member of this group')
    return True

def validate_group_message_member(group_member):
    if not group_member.exists():
        raise ValidationError('User is not a member of this group')
    return True

def validate_group_message_sender(group_member, group_message):
    if group_member.member.id != group_message.message.sender.id:
        raise PermissionDenied('You are not allowed to modify or unsend this message')
    return True

def validate_update_chat_message(chat_message, sender_id):
    if chat_message.message.sender.id != sender_id:
        raise PermissionDenied('You are not allowed to update this message')
    return True

def validate_delete_chat_message(chat_message, sender_id):
    if chat_message.chat.user.id != sender_id:
        raise PermissionDenied('You are not allowed to delete this message')
    return True

def validate_unsend_chat_message(chat_message, sender_id):
    if chat_message.message.sender.id != sender_id:
        raise PermissionDenied('You are not allowed to unsend this message')
    return True

def validate_delete_chat(chat_id, user):
    chat = get_object_or_404(Chat, pk=chat_id)
    if chat.user.id != user.id:
        raise PermissionDenied('You are not allowed to delete this chat')
    return True

def validate_group_title(title):
    if len(title) < 2:
        raise ValidationError('Group title must be at least 2 characters long')
    return True

def validate_group_description(description):
    if len(description) < 10:
        raise ValidationError('Group description must be at least 10 characters long')
    return True

def validate_admin(user_group, group_admin):
    if not user_group.members.filter(pk=group_admin.pk).exists():
        raise ValidationError('User is not a member of this group')
    if not group_admin.is_admin:
        raise PermissionDenied('User is not an admin of this group')
    return True
    