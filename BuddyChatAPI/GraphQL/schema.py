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
    
    def resolve_chats(self, info, **kwargs):
        return get_chats()
    
    def resolve_user_groups(self, info, **kwargs):
        return get_user_groups()
    
    def resolve_chat(self, info, id):
        return get_chat(id)
    
    def resolve_user_group(self, info, id):
        return get_user_group(id)
    
    def resolve_user(self, info, id):
        return get_user(id)
    
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_chat = CreateChat.Field()
    create_chat_message = CreateChatMessage.Field()
    create_group = CreateGroup.Field()
    create_group_message = CreateGroupMessage.Field()
    create_group_member = CreateGroupMember.Field()
    assign_admin = AssignAdmin.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

