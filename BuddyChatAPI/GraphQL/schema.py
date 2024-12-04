import graphene
from graphene_django import DjangoListField
from .connections import CustomUserConnection, ChatConnection, UserGroupConnection
from .types import CustomUserType, ChatType, UserGroupType, NotificationType
from .mutations import *
from .resolvers import get_chat, get_user_group, get_user, get_users, get_chats, get_user_groups
    
class Query(graphene.ObjectType):
    users = graphene.relay.ConnectionField(CustomUserConnection)
    chats = graphene.relay.ConnectionField(ChatConnection)
    user_groups = graphene.relay.ConnectionField(UserGroupConnection)
    notifications = DjangoListField(NotificationType)
    
    chat = graphene.Field(ChatType, id=graphene.Int())
    user_group = graphene.Field(UserGroupType, id=graphene.Int())
    user = graphene.Field(CustomUserType, id=graphene.Int())
    
    def resolve_users(self, info, **kwargs):
        return get_users()
    
    @login_required
    def resolve_chats(self, info, **kwargs):
        return get_chats().filter(user1=info.context.user) | get_chats().filter(user2=info.context.user)
    
    @login_required
    def resolve_user_groups(self, info, **kwargs):
        group_member = GroupMember.objects.filter(member=info.context.user)
        return get_user_groups().filter(pk__in=group_member.values_list('user_group', flat=True))
    
    @login_required
    def resolve_chat(self, info, id):
        chat = get_chat(id)
        if chat.user1 == info.context.user or chat.user2 == info.context.user:
            return chat
        raise PermissionDenied("You are not allowed to view this chat")
    
    @login_required
    def resolve_user_group(self, info, id):
        user_group = get_user_group(id)
        group_members = GroupMember.objects.filter(user_group=user_group)
        users = group_members.values_list('member', flat=True)
        usernames = CustomUser.objects.filter(pk__in=users).values_list('username', flat=True)
        if info.context.user.username in usernames:
            return user_group
        raise PermissionDenied("You are not allowed to view this group")
    
    def resolve_user(self, info, id):
        return get_user(id)
    
class Mutation(AuthMutation, graphene.ObjectType):
    create_user = CreateUser.Field()
    create_chat = CreateChat.Field()
    create_chat_message = CreateChatMessage.Field()
    create_group = CreateGroup.Field()
    create_group_message = CreateGroupMessage.Field()
    create_group_member = CreateGroupMember.Field()
    assign_admin = AssignAdmin.Field()
    set_notification_read = SetNotificationAsRead.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

