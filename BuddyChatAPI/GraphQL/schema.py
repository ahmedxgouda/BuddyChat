import graphene
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
    user_groups = DjangoFilterConnectionField(UserGroupMemberCopyType, fields=['is_archived'])
    notifications = DjangoFilterConnectionField(NotificationType, fields=['is_read'])
    
    chat = graphene.Field(ChatType, id=graphene.Int())
    user_group = graphene.Field(UserGroupType, id=graphene.Int())
    user = graphene.Field(CustomUserType, id=graphene.Int())
    
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()
    
    @login_required
    def resolve_chats(self, info, **kwargs):
        return Chat.objects.filter(user=info.context.user)
    
    @login_required
    def resolve_user_groups(self, info, **kwargs):
        group_member = GroupMember.objects.filter(member=info.context.user)
        user_groups = UserGroupMemberCopy.objects.filter(member__in=group_member)
        return user_groups
    
    @login_required
    def resolve_chat(self, info, id):
        chat = Chat.objects.get(pk=id)
        if chat.user == info.context.user:
            return chat
        raise PermissionDenied("You are not allowed to view this chat")
    
    @login_required
    def resolve_user_group(self, info, id):
        user_group = UserGroupMemberCopy.objects.get(pk=id)
        if user_group.member.member.id == info.context.user.id:
            return user_group
        raise PermissionDenied("You are not allowed to view this group")
    
    def resolve_user(self, info, id):
        return CustomUser.objects.get(pk=id)
    
class Mutation(AuthMutation, GroupMutations, ChatMutations, graphene.ObjectType):
    set_notification_read = SetNotificationAsRead.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

