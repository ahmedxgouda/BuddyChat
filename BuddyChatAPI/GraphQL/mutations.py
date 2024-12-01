from django.shortcuts import get_object_or_404
import graphene
from ..models import *
from .types import CustomUserType, MessageType, ChatType, UserGroupType
from .validators import validate_user_data, validate_message_content, validate_chat_users
import bleach

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        phone = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    def mutate(self, info, username, email, password, phone, first_name, last_name):
        validate_user_data(username, email, password, phone, first_name, last_name)
        user = CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone, first_name=first_name, last_name=last_name)
        user.save()
        return CreateUser(user=user)

class CreateMessage(graphene.Mutation):
    class Arguments:
        sender_id = graphene.Int()
        receiver_id = graphene.Int()
        content = graphene.String()
        
    message = graphene.Field(MessageType)
    
    def mutate(self, info, sender_id, receiver_id, content):
        sender = get_object_or_404(CustomUser, pk=sender_id)
        receiver = get_object_or_404(CustomUser, pk=receiver_id)
        content = bleach.clean(content)
        validate_message_content(content)
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        message.save()
        return CreateMessage(message=message)

class CreateChat(graphene.Mutation):
    class Arguments:
        user1_id = graphene.Int()
        user2_id = graphene.Int()
        
    chat = graphene.Field(ChatType)
    
    def mutate(self, info, user1_id, user2_id):
        user1 = get_object_or_404(CustomUser, pk=user1_id)
        user2 = get_object_or_404(CustomUser, pk=user2_id)
        validate_chat_users(user1, user2)
        chat = Chat.objects.create(user1=user1, user2=user2)
        chat.save()
        return CreateChat(chat=chat)