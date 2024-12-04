from django.shortcuts import get_object_or_404
import graphene
from ..models import *
from .types import *
from .validators import *
import bleach
from graphql_jwt.decorators import login_required
from graphql_jwt import Verify, Refresh, ObtainJSONWebToken
from graphql_jwt.exceptions import JSONWebTokenError
from allauth.account.models import EmailAddress

def create_message(sender_id, content):
    sender = get_object_or_404(CustomUser, pk=sender_id)
    content = bleach.clean(content)
    validate_message_content(content)
    message = Message.objects.create(sender=sender, content=content)
    message.save()
    return message

def create_group_member(user_group_id, member_id, is_admin=False):
    user_group = get_object_or_404(UserGroup, pk=user_group_id)
    member = get_object_or_404(CustomUser, pk=member_id)
    validate_group_member(user_group, member)
    group_member = GroupMember.objects.create(user_group=user_group, member=member, is_admin=is_admin)
    group_member.save()
    user_group.members_count += 1
    user_group.save()
    return group_member


class ObtainJSONWebTokenCustom(ObtainJSONWebToken):
    @classmethod
    def resolve(cls, root, info, **kwargs):
        response = super().resolve(root, info, **kwargs)
        user = info.context.user
        if not user.is_authenticated:
            raise JSONWebTokenError('Please, enter valid credentials')
        # if not EmailAddress.objects.filter(user=user, verified=True).exists():
        #     raise JSONWebTokenError('Please, verify your email address')
        return response
    
class AuthMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebTokenCustom.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        phone = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    def mutate(self, info, username, email, password, phone, first_name, last_name):
        validate_user_data(username, email, password, phone, first_name, last_name)
        user = CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone, first_name=first_name, last_name=last_name)
        user.save()
        return CreateUser(user=user)
class CreateChat(graphene.Mutation):
    class Arguments:
        user1_id = graphene.Int()
        user2_id = graphene.Int()
        
    chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, user1_id, user2_id):
        user1 = get_object_or_404(CustomUser, pk=user1_id)
        user2 = get_object_or_404(CustomUser, pk=user2_id)
        validate_chat_users(user1, user2)
        chat = Chat.objects.create(user1=user1, user2=user2)
        chat.save()
        return CreateChat(chat=chat)
    
class CreateChatMessage(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_id, content):
        chat = get_object_or_404(Chat, pk=chat_id)
        sender_id = info.context.user.id
        validate_chat_message(chat, sender_id)
        message = create_message(sender_id, content)
        chat_message = ChatMessage.objects.create(chat=chat, message=message)
        chat_message.save()
        chat.last_message = chat_message
        chat.save()
        receiver = chat.user1 if chat.user1_id != sender_id else chat.user2
        notification = Notification.objects.create(receiver=receiver, message=message)
        notification.save()
        return CreateChatMessage(chat_message=chat_message)
    
class CreateGroup(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        
    user_group = graphene.Field(UserGroupType)
    
    @login_required
    def mutate(self, info, title):
        created_by_id = info.context.user.id
        created_by = CustomUser.objects.get(pk=created_by_id)
        validate_group_title(title)
        title = bleach.clean(title)
        user_group = UserGroup.objects.create(title=title, created_by=created_by)
        user_group.save()
        create_group_member(user_group.id, created_by_id, is_admin=True)
        return CreateGroup(user_group=user_group)
    
class CreateGroupMessage(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    @login_required
    def mutate(self, info, user_group_id, content):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        sender_id = info.context.user.id
        # check if the sender is a member of the group
        validate_group_message_sender(user_group, sender_id)
        content = bleach.clean(content)
        validate_message_content(content)
        message = create_message(sender_id, content)
        group_message = GroupMessage.objects.create(user_group=user_group, message=message)
        group_message.save()
        # Update last message of the group
        user_group.last_message = group_message
        user_group.save()
        # Send notifications to group members
        for group_member in user_group.members.all():
            if group_member.member.id != sender_id:
                notification = Notification.objects.create(receiver=group_member.member, message=message)
                notification.save()
        return CreateGroupMessage(group_message=group_message)
    
class CreateGroupMember(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        member_id = graphene.Int()
        
    group_member = graphene.Field(GroupMemberType)
    
    @login_required
    def mutate(self, info, user_group_id, member_id):
        validate_admin(user_group_id, member_id, info.context.user)
        group_member = create_group_member(user_group_id, member_id)
        return CreateGroupMember(group_member=group_member)

class AssignAdmin(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        member_id = graphene.Int()
        
    group_member = graphene.Field(GroupMemberType)
    
    @login_required
    def mutate(self, info, user_group_id, member_id):
        group_member = get_object_or_404(GroupMember, user_group_id=user_group_id, member_id=member_id)
        validate_admin(group_member, user_group_id, info.context.user)
        group_member.is_admin = True
        group_member.save()
        return AssignAdmin(group_member=group_member)

class SetNotificationAsRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int()
        
    notification = graphene.Field(NotificationType)
    
    @login_required
    def mutate(self, info, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id)
        notification.is_read = True
        return SetNotificationAsRead(notification=notification)
