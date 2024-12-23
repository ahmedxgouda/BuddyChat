from graphene_django import DjangoObjectType
from ..models import *
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied
class CustomUserType(DjangoObjectType):
    """The user type. It contains the user's information"""
    class Meta:
        model = CustomUser
        exclude = ('password', 'other_user_chats', 'is_superuser', 'is_staff', 'groups')
        interfaces = (graphene.relay.Node, )
        
    notifications = DjangoFilterConnectionField('BuddyChatAPI.GraphQL.types.NotificationType', fields=['is_read'], max_limit=20)
    email = graphene.String()
    phone_numbers = graphene.List('BuddyChatAPI.GraphQL.types.PhoneNumberType')
    chats = DjangoFilterConnectionField('BuddyChatAPI.GraphQL.types.ChatType', fields=['archived'], max_limit=20)
    
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
    def resolve_phone_numbers(self, info):
        if self == info.context.user:
            return self.phone_numbers.all()
        raise PermissionDenied('Only the user can view their phone numbers')
    
    @login_required
    def resolve_chats(self, info):
        if self == info.context.user:
            return self.chats.all()
        raise PermissionDenied('Only the user can view their chats')

        
class PhoneNumberType(DjangoObjectType):
    class Meta:
        model = PhoneNumber
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class PhoneNumberInputType(graphene.InputObjectType):
    number = graphene.String(required=True)
    country_code = graphene.String(required=True)

class MessageType(DjangoObjectType):
    """The root message type which is the dependent type for the chat message and group message types"""
    class Meta:
        model = Message
        fields = "__all__"
        interfaces = (graphene.relay.Node, )
        

class ChatType(DjangoObjectType):
    """The chat type. Each user has a chat copy for each other user they have chatted with"""
    class Meta:
        model = Chat
        fields = "__all__"
        interfaces = (graphene.relay.Node, )
        
class ChatMessageType(DjangoObjectType):
    """The chat message type. It contains the chat message information"""
    class Meta:
        model = ChatMessage
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class UserGroupType(DjangoObjectType):
    """The root user group type. It contains the main information. GroupMemberType depends on this type"""
    class Meta:
        model = UserGroup
        fields = "__all__"
        interfaces = (graphene.relay.Node, )
class GroupMessageType(DjangoObjectType):
    """The group message type. It contains the group message information"""
    class Meta:
        model = GroupMessage
        fields = "__all__"
        interfaces = (graphene.relay.Node, )
class GroupMemberType(DjangoObjectType):
    """The group member type. It contains the group member information"""
    class Meta:
        model = GroupMember
        fields = "__all__"
        interfaces = (graphene.relay.Node, )
        
class AttachmentType(DjangoObjectType):
    class Meta:
        model = Attachment
        fields = "__all__"
        
class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class UserGroupMemberCopyType(DjangoObjectType):
    """The user group member copy type. The user copy of the group, so that each user can have a copy of the group messages"""
    class Meta:
        model = UserGroupMemberCopy
        fields = "__all__"
        interfaces = (graphene.relay.Node, )

class SubsctiptionType(graphene.ObjectType):
    """The subscription type"""
    success = graphene.Boolean()