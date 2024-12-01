from ..models import *

def get_users():
    return CustomUser.objects.all()

def get_chats():
    return Chat.objects.all()

def get_user_groups():
    return UserGroup.objects.all()

def get_chat(id):
    return Chat.objects.get(pk=id)

def get_user_group(id):
    return UserGroup.objects.get(pk=id)

def get_user(id):
    return CustomUser.objects.get(pk=id)

