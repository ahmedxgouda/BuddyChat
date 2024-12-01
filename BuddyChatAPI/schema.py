import graphene
from graphene_django import DjangoObjectType, DjangoListField
from .models import *
from .validators import validate_user_data, validate_message_content
from django.shortcuts import get_object_or_404
import bleach

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('password',)
        
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
class CustomUserConnection(graphene.relay.Connection):
    class Meta:
        node = CustomUserType
        
class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"
        
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

class ChatType(DjangoObjectType):
    class Meta:
        model = Chat
        fields = "__all__"
        
class ChatConnection(graphene.relay.Connection):
    class Meta:
        node = ChatType
class ChatMessageType(DjangoObjectType):
    class Meta:
        model = ChatMessage
        fields = "__all__"
        
class UserGroupType(DjangoObjectType):
    class Meta:
        model = UserGroup
        fields = "__all__"
        
class UserGroupConnection(graphene.relay.Connection):
    class Meta:
        node = UserGroupType
class GroupMessageType(DjangoObjectType):
    class Meta:
        model = GroupMessage
        fields = "__all__"
        
class GroupMemberType(DjangoObjectType):
    class Meta:
        model = GroupMember
        fields = "__all__"
        
class AttachmentType(DjangoObjectType):
    class Meta:
        model = Attachment
        fields = "__all__"
        
class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"
    
class Query(graphene.ObjectType):
    users = graphene.relay.ConnectionField(CustomUserConnection)
    chats = graphene.relay.ConnectionField(ChatConnection)
    user_groups = graphene.relay.ConnectionField(UserGroupConnection)
    notifications = DjangoListField(NotificationType)
    
    chat = graphene.Field(ChatType, id=graphene.Int())
    user_group = graphene.Field(UserGroupType, id=graphene.Int())
    user = graphene.Field(CustomUserType, id=graphene.Int())
    
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()
    
    def resolve_chats(self, info, **kwargs):
        return Chat.objects.all()
    
    def resolve_user_groups(self, info, **kwargs):
        return UserGroup.objects.all()
    
    def resolve_chat(self, info, id):
        return Chat.objects.get(pk=id)
    
    def resolve_user_group(self, info, id):
        return UserGroup.objects.get(pk=id)
    
    def resolve_user(self, info, id):
        return CustomUser.objects.get(pk=id)
    
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_message = CreateMessage.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

