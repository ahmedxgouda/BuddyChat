import graphene
from graphene.relay.node import Node
from graphene_django.filter import DjangoFilterConnectionField
from .types import CustomUserType, ChatType, NotificationType, UserGroupMemberCopyType, ChatMessageType
from .mutations.notification_mutations import SetNotificationAsRead
from .mutations.auth_mutations import AuthMutation
from .mutations.group_mutations import GroupMutations
from .mutations.chat_mutations import ChatMutations
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, GroupMember, Chat, UserGroupMemberCopy, ChatMessage
from channels.layers import get_channel_layer
    
class Query(graphene.ObjectType):
    users = DjangoFilterConnectionField(CustomUserType, fields=['username', 'first_name', 'last_name'], max_limit=20)
    chats = DjangoFilterConnectionField(ChatType, fields=['archived'], max_limit=20)
    groups = DjangoFilterConnectionField(UserGroupMemberCopyType, fields=['is_archived'], max_limit=20)
    notifications = DjangoFilterConnectionField(NotificationType, fields=['is_read'], max_limit=20)
    
    chat = graphene.Field(ChatType, id=graphene.ID())
    group = graphene.Field(UserGroupMemberCopyType, id=graphene.ID())
    user = graphene.Field(CustomUserType, id=graphene.ID())
    
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()
    
    @login_required
    def resolve_chats(self, info, **kwargs):
        return Chat.objects.filter(user=info.context.user)
    
    @login_required
    def resolve_groups(self, info, **kwargs):
        group_member = GroupMember.objects.filter(member=info.context.user)
        user_groups = UserGroupMemberCopy.objects.filter(member__in=group_member)
        return user_groups
    
    @login_required
    def resolve_chat(self, info, id):
        chat: Chat = Node.get_node_from_global_id(info, id)
        if chat.user == info.context.user:
            return chat
        raise PermissionDenied("You are not allowed to view this chat")
    
    @login_required
    def resolve_group(self, info, id):
        user_group: UserGroupMemberCopy = Node.get_node_from_global_id(info, id)
        if user_group.member.member.id == info.context.user.id:
            return user_group
        raise PermissionDenied("You are not allowed to view this group")
    
    def resolve_user(self, info, id):
        user: CustomUser = Node.get_node_from_global_id(info, id)
        return user
    
class Mutation(AuthMutation, GroupMutations, ChatMutations, graphene.ObjectType):
    set_notification_read = SetNotificationAsRead.Field()
    
class Subscription(graphene.ObjectType):
    chat_message = graphene.Field(ChatMessageType)
    
    # @login_required
    async def resolve_chat_message(root, info):
        channel_layer = get_channel_layer()
        message = await channel_layer.receive(f"user_{info.context.user.username}")
        print(message)
        yield ChatMessage.objects.get(id=message['data']['payload']['id'])
    
schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)

