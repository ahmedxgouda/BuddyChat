import graphene
from graphene.relay.node import Node
from graphene_django.filter import DjangoFilterConnectionField
from .types import CustomUserType, ChatType, NotificationType, UserGroupMemberCopyType, SubsctiptionType
from .mutations.notification_mutations import SetNotificationAsRead
from .mutations.auth_mutations import AuthMutation
from .mutations.group_mutations import GroupMutations
from .mutations.chat_mutations import ChatMutations
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, GroupMember, Chat, UserGroupMemberCopy, ChatMessage, Message
from channels.db import database_sync_to_async
import asyncio
    
class Query(graphene.ObjectType):
    """The Root Query for the GraphQL API"""
    
    users = DjangoFilterConnectionField(CustomUserType, fields=['username', 'first_name', 'last_name'], max_limit=20, description="The users in the system")
    chats = DjangoFilterConnectionField(ChatType, fields=['archived'], max_limit=20, description="The chats for the current user")
    groups = DjangoFilterConnectionField(UserGroupMemberCopyType, fields=['is_archived'], max_limit=20, description="The group copies for the current user")
    notifications = DjangoFilterConnectionField(NotificationType, fields=['is_read'], max_limit=20, description="The notifications for the current user")
    
    chat = graphene.Field(ChatType, id=graphene.ID(), description="Resolve a chat for the current user")
    group = graphene.Field(UserGroupMemberCopyType, id=graphene.ID(), description="Resolve a group copy for the current user")
    user = graphene.Field(CustomUserType, id=graphene.ID(), description="Resolve a user")
        
    @login_required
    def resolve_chats(self, info, **kwargs):
        """Resolves the chats for the current user"""
        return Chat.objects.filter(user=info.context.user).select_related('user', 'other_user').prefetch_related('chat_messages__message__sender__phone_numbers')
    
    @login_required
    def resolve_groups(self, info, **kwargs):
        """Resolves the group copies for the current user"""
        group_member = GroupMember.objects.filter(member=info.context.user)
        user_groups = UserGroupMemberCopy.objects.filter(member__in=group_member).select_related('member__user_group__created_by', 'member__member').prefetch_related('member__user_group__members__member__phone_numbers')
        return user_groups
    
    @login_required
    def resolve_chat(self, info, id):
        """Resolves a chat for the current user"""
        chat: Chat = Node.get_node_from_global_id(info, id)
        if chat.user == info.context.user:
            return chat
        raise PermissionDenied("You are not allowed to view this chat")
    
    @login_required
    def resolve_group(self, info, id):
        """Resolves a group copy for the current user"""
        user_group: UserGroupMemberCopy = Node.get_node_from_global_id(info, id)
        if user_group.member.member.id == info.context.user.id:
            return user_group
        raise PermissionDenied("You are not allowed to view this group")
    
    def resolve_user(self, info, id):
        """Resolves a user"""
        user: CustomUser = Node.get_node_from_global_id(info, id)
        return user
    
class Mutation(AuthMutation, GroupMutations, ChatMutations, graphene.ObjectType):
    """The Root Mutation for the GraphQL API"""
    set_notification_read = SetNotificationAsRead.Field(description="Set a notification as read")
    
class Subscription(graphene.ObjectType):
    """The Root Subscription for the GraphQL API"""
    subscribe = graphene.Field(SubsctiptionType, description="The subscription for the API")
    
    async def subscribe_subscribe(root, info):
        """Subscribes to the subscription"""
        yield {
            'success': True
        }
            
            
    
schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
