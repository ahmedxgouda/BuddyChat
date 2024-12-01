from django.core.exceptions import ValidationError
from ..models import CustomUser, Chat

def validate_user_data(username, email, password, phone, first_name, last_name):
    
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError('Username already exists')
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError('Email already exists')
    if CustomUser.objects.filter(phone=phone).exists():
        raise ValidationError('Phone number already exists')
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if len(phone) != 13:
        raise ValidationError('Phone number must be 13 characters long')
    if len(first_name) < 2:
        raise ValidationError('First name must be at least 2 characters long')
    if len(last_name) < 2:
        raise ValidationError('Last name must be at least 2 characters long')
    return True

def validate_message_content(content):
    if len(content) < 1:
        raise ValidationError('Message content cannot be empty')
    return True

def validate_chat_users(user1, user2):
    if Chat.objects.filter(user1=user1, user2=user2).exists() or Chat.objects.filter(user1=user2, user2=user1).exists():
        raise ValidationError('Chat already exists')
    
def validate_group_member(user_group, member):
    if user_group.members.filter(pk=member.pk).exists():
        raise ValidationError('User is already a member of this group')
    return True

def validate_chat_message(chat: Chat, sender_id, receiver_id):
    # Case 1: A user is trying to send a message to themselves
    # Case 2: A user is trying to send a message to a user who is not a member of the chat
    if chat.user1.pk == sender_id and chat.user2.pk == receiver_id:
        return True
    if chat.user1.pk == receiver_id and chat.user2.pk == sender_id:
        return True
    raise ValidationError(f'A user is not a member of this chat')
