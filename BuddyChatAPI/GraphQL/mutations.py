from django.shortcuts import get_object_or_404
import graphene
from ..models import *
from .types import *
from .validators import *
import bleach

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
        sender_id = graphene.Int()
        receiver_id = graphene.Int()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    def mutate(self, info, chat_id, sender_id, content, receiver_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        validate_chat_message(chat, sender_id, receiver_id)
        message = create_message(sender_id, receiver_id, content)
        chat_message = ChatMessage.objects.create(chat=chat, message=message)
        chat_message.save()
        receiver = get_object_or_404(CustomUser, pk=receiver_id)
        notification = Notification.objects.create(receiver=receiver, message=message)
        notification.save()
        return CreateChatMessage(chat_message=chat_message)
    
class CreateGroup(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        created_by_id = graphene.Int()
        
    user_group = graphene.Field(UserGroupType)
    
    def mutate(self, info, title, created_by_id):
        created_by = get_object_or_404(CustomUser, pk=created_by_id)
        validate_group_title(title)
        title = bleach.clean(title)
        user_group = UserGroup.objects.create(title=title, created_by=created_by)
        user_group.save()
        create_group_member(user_group.id, created_by_id, is_admin=True)
        return CreateGroup(user_group=user_group)
    
class CreateGroupMessage(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        sender_id = graphene.Int()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    def mutate(self, info, user_group_id, sender_id, content):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        content = bleach.clean(content)
        validate_message_content(content)
        message = create_message(sender_id, None, content)
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
    
    def mutate(self, info, user_group_id, member_id):
        group_member = create_group_member(user_group_id, member_id)
        return CreateGroupMember(group_member=group_member)

class AssignAdmin(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        member_id = graphene.Int()
        
    group_member = graphene.Field(GroupMemberType)
    
    def mutate(self, info, user_group_id, member_id):
        group_member = get_object_or_404(GroupMember, user_group_id=user_group_id, member_id=member_id)
        validate_admin_assignment(group_member, user_group_id, info.context.user)
        group_member.is_admin = True
        group_member.save()
        return AssignAdmin(group_member=group_member)

class SetNotificationAsRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int()
        
    notification = graphene.Field(NotificationType)
    
    def mutate(self, info, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id)
        notification.is_read = True
        return SetNotificationAsRead(notification=notification)
