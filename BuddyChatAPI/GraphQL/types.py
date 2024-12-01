from graphene_django import DjangoObjectType
from ..models import *

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('password',)
        
        
class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"
        

class ChatType(DjangoObjectType):
    class Meta:
        model = Chat
        fields = "__all__"
        
class ChatMessageType(DjangoObjectType):
    class Meta:
        model = ChatMessage
        fields = "__all__"
        
class UserGroupType(DjangoObjectType):
    class Meta:
        model = UserGroup
        fields = "__all__"
        
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
