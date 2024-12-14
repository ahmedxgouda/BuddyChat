import graphene
from graphene.relay.node import Node
from graphene_django.filter import DjangoFilterConnectionField
from .types import CustomUserType, ChatType, UserGroupType, NotificationType, UserGroupMemberCopyType
from .mutations.notification_mutations import SetNotificationAsRead
from .mutations.auth_mutations import AuthMutation
from .mutations.group_mutations import GroupMutations
from .mutations.chat_mutations import ChatMutations
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..models import CustomUser, GroupMember, Chat, UserGroupMemberCopy, Notification
    
class Query(graphene.ObjectType):
    users = DjangoFilterConnectionField(CustomUserType, fields=['username', 'first_name', 'last_name'])
    chats = DjangoFilterConnectionField(ChatType, fields=['archived'])
    groups = DjangoFilterConnectionField(UserGroupMemberCopyType, fields=['is_archived'])
    notifications = DjangoFilterConnectionField(NotificationType, fields=['is_read'])
    
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
    
schema = graphene.Schema(query=Query, mutation=Mutation)

