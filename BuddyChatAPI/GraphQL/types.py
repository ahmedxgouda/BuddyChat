from graphene_django import DjangoObjectType
from ..models import *
import graphene
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied
class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('password',)
        
    notifications = graphene.List('BuddyChatAPI.GraphQL.types.NotificationType')
    email = graphene.String()
    phone = graphene.String()
    
    @login_required
    def resolve_notifications(self, info):
        if self == info.context.user:
            return self.notifications.all()
        raise PermissionDenied('Only the user can view their notifications')
    
    @login_required
    def resolve_email(self, info):
        if self == info.context.user:
            return self.email
        raise PermissionDenied('Only the user can view their email')
    
    @login_required
    def resolve_phone(self, info):
        if self == info.context.user:
            return self.phone
        raise PermissionDenied('Only the user can view their phone number')
        
        
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
