from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType
import graphene
from ..models import *
from .types import CustomUserType, MessageType
from ..validators import validate_user_data, validate_message_content
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
