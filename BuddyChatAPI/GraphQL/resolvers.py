from ..models import *

def get_users():
    return CustomUser.objects.all().select_related('sent_messages', 'received_messages', 'user1_chats', 'user2_chats', 'created_groups', 'user_groups', 'notifications')

def get_chats():
    return Chat.objects.all().select_related('last_message')

def get_user_groups():
    return UserGroup.objects.all()

def get_chat(id):
    return Chat.objects.get(pk=id)

def get_user_group(id):
    return UserGroup.objects.get(pk=id)

def get_user(id):
    return CustomUser.objects.get(pk=id)

