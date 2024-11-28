import graphene
from graphene_django import DjangoObjectType, DjangoListField
from .models import *

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('password',)
        
class CustomUserConnection(graphene.relay.Connection):
    class Meta:
        node = CustomUserType
        
class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"
        
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
    
schema = graphene.Schema(query=Query)

