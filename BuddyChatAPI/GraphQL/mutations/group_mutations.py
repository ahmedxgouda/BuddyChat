import graphene
import bleach
from graphql_jwt.decorators import login_required
from ..validators import validate_group_title, validate_group_message_sender, validate_admin, validate_message_content, validate_group_description, validate_group_creator, validate_group_copy_member, validate_group_member
from ..helpers import create_group_member, create_message, get_node_or_error
from ...models import UserGroup, GroupMember, GroupMessage, Notification, CustomUser, UserGroupMemberCopy
from ..types import UserGroupType, GroupMemberType, GroupMessageType, UserGroupMemberCopyType, MessageType
from django.utils import timezone
from graphene.relay import Node
from ..subscriptions.signals import on_message_created, on_message_updated, on_message_deleted, on_message_unsent, on_notification_created, on_chat_deleted, on_group_updated, on_group_removed, on_member_added, on_member_removed
from django.db.models.signals import ModelSignal

class CreateGroup(graphene.Mutation):
    """A mutation to create a group. The creator is automatically added as an admin, and a group member copy is created for the creator"""
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
        global_id = Node.to_global_id('CustomUserType', created_by_id)
        create_group_member(user_group, global_id, info, is_admin=True)
        user_group.save()
        return CreateGroup(user_group=user_group)
    
class CreateGroupMessage(graphene.Mutation):
    """A mutation to create a group message. A group message is created for each group member, and a notification is created for each group member"""
    class Arguments:
        group_copy_id = graphene.ID()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    @login_required
    def mutate(self, info, group_copy_id, content):
        group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        group_member = group_copy.member
        user_group = group_copy.member.user_group
        sender_id = info.context.user.id
        
        # check if the sender is a member of the group
        validate_group_message_sender(group_member, sender_id)
        content = bleach.clean(content)
        validate_message_content(content)
        message = create_message(sender_id, content)
        user_group_message = GroupMessage.objects.create(message=message, user_group_copy=group_copy)
        user_group_message.save()
        ModelSignal.send(on_message_created, sender=GroupMessage, instance=user_group_message, is_chat=False)
        # Create group message for each group member - for deleting and unsending messages
        for group_member in user_group.members.all():
            if group_member.member.id == sender_id:
                continue
            group_member_copy = UserGroupMemberCopy.objects.get(member=group_member)
            group_message = GroupMessage.objects.create(message=message, user_group_copy=group_member_copy)
            group_message.save()
            group_member_copy.last_message = group_message
            group_member_copy.save()
            notification = Notification.objects.create(receiver=group_member.member, message=message)
            notification.save()
            ModelSignal.send(on_message_created, sender=GroupMessage, instance=group_message, is_chat=False)
            ModelSignal.send(on_notification_created, sender=Notification, instance=notification)
        return CreateGroupMessage(group_message=user_group_message)
    
class CreateGroupMember(graphene.Mutation):
    """A mutation to add a member to a group"""
    class Arguments:
        group_copy_id = graphene.ID()
        member_id = graphene.ID()
        
    group_member = graphene.Field(GroupMemberType)
    
    @login_required
    def mutate(self, info, group_copy_id, member_id):
        group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        user_group = group_copy.member.user_group
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        group_member = create_group_member(user_group, member_id, info)
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            ModelSignal.send(on_member_added, member_copy=group_member_copy, new_member=group_member, username=group_member_copy.member.member.username, sender=GroupMember)
        return CreateGroupMember(group_member=group_member)

class ChangeAdmin(graphene.Mutation):
    """A mutation to change the admin status of a group member"""
    class Arguments:
        group_copy_id = graphene.ID()
        member_id = graphene.ID()
        is_admin = graphene.Boolean()
        
    group_member = graphene.Field(GroupMemberType)
    
    @login_required
    def mutate(self, info, group_copy_id, member_id, is_admin):
        group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        user_group = group_copy.member.user_group
        group_member: GroupMember = get_node_or_error(info, member_id)
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        validate_group_member(user_group, group_member)
        group_member.is_admin = is_admin
        group_member.save()
        return ChangeAdmin(group_member=group_member)
    
class UpdateGroup(graphene.Mutation):
    """A mutation to update a group"""
    class Arguments:
        group_copy_id = graphene.ID()
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        group_image = graphene.String(required=False)
        
    group_copy = graphene.Field(UserGroupMemberCopyType)
    
    @login_required
    def mutate(self, info, group_copy_id, title=None, description=None, group_image=None):
        user_group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        user_group = user_group_copy.member.user_group
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        if title:
            validate_group_title(title)
            title = bleach.clean(title)
            user_group.title = title
        if description:
            validate_group_description(description)
            user_group.description = bleach.clean(description)
        if group_image:
            user_group.group_image = group_image
        if title or description or group_image:
            user_group.updated_at = timezone.now()
            user_group.save()
            
            for member in user_group.members.all():
                group_member_copy = UserGroupMemberCopy.objects.get(member=member)
                ModelSignal.send(on_group_updated, sender=UserGroupMemberCopy, instance=group_member_copy)
        return UpdateGroup(group_copy=user_group_copy)

class DeleteGroup(graphene.Mutation):
    """A mutation to delete a group. Messages are deleted for the group copy of the current user"""
    class Arguments:
        group_copy_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_copy_id):
        user_group_copy = get_node_or_error(info, group_copy_id)
        validate_group_copy_member(user_group_copy, info.context.user)
        for group_message in user_group_copy.group_messages.all():
            group_message.delete()
        ModelSignal.send(on_chat_deleted, sender=UserGroupMemberCopy, instance=user_group_copy, is_chat=False)
        return DeleteGroup(success=True)

class UpdateGroupMessage(graphene.Mutation):
    """A mutation to update a group message"""
    class Arguments:
        group_message_id = graphene.ID()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    @login_required
    def mutate(self, info, group_message_id, content):
        user_group_message: GroupMessage = get_node_or_error(info, group_message_id)
        group_member = user_group_message.user_group_copy.member
        validate_group_message_sender(group_member, user_group_message.message.sender.id)
        content = bleach.clean(content)
        validate_message_content(content)
        user_group_message.message.content = content
        user_group_message.message.save()
        # Send signals to update the message for all group members
        user_group = user_group_message.user_group_copy.member.user_group
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            group_message = GroupMessage.objects.get(message=user_group_message.message, user_group_copy=group_member_copy)
            ModelSignal.send(on_message_updated, sender=GroupMessage, instance=group_message, is_chat=False)
        return UpdateGroupMessage(group_message=user_group_message)

class DeleteGroupMessage(graphene.Mutation):
    """A mutation to delete a group message. Deletes the message for the group copy of the current user"""
    class Arguments:
        group_message_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_message_id):
        group_message = get_node_or_error(info, group_message_id)
        last_message_id = group_message.user_group_copy.last_message.id
        chat_id = group_message.user_group_copy.id
        group_message.delete()
        if last_message_id == group_message.id:
            group_message.user_group_copy.last_message = group_message.user_group_copy.group_messages.first()
            group_message.user_group_copy.save()
        ModelSignal.send(on_message_deleted, sender=GroupMessage, message_id=group_message_id, is_chat=False, chat_id=chat_id, username=info.context.user.username)
        return DeleteGroupMessage(success=True)

class UnsendGroupMessage(graphene.Mutation):
    """A mutation to unsend a group message. Deletes the message for all group members"""
    class Arguments:
        group_message_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_message_id):
        group_message = get_node_or_error(info, group_message_id)
        group_member = group_message.user_group_copy.member
        validate_group_message_sender(group_member, group_message.message.sender.id)
        last_message_id = group_message.user_group_copy.last_message.message.id
        user_group = group_message.user_group_copy.member.user_group
        group_messages = []
        # Update last message for all group members
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            if last_message_id == group_member_copy.last_message.message.id:
                group_member_copy.last_message = group_member_copy.group_messages.first()
                group_member_copy.save()
            group_messages += group_member_copy.group_messages.filter(message=group_message.message)
                
        group_message.message.delete()
        for group_message in group_messages:
            ModelSignal.send(on_message_unsent, sender=GroupMessage, instance=group_message, is_chat=False)
        
        return UnsendGroupMessage(success=True)
    
class RemoveGroupMember(graphene.Mutation):
    """A mutation to remove a member from a group"""
    class Arguments:
        group_copy_id = graphene.ID()
        member_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_copy_id, member_id):
        group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        user_group = group_copy.member.user_group
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        group_member: GroupMember = get_node_or_error(info, member_id)
        validate_group_member(user_group, group_member)
        group_member.delete()
        user_group.members_count -= 1
        user_group.save()
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            ModelSignal.send(on_member_removed, member_copy=group_member_copy, member_id=member_id, username=group_member_copy.member.member.username, removed_by_id=info.context.user.id, sender=GroupMember)
        return RemoveGroupMember(success=True)

class LeaveGroup(graphene.Mutation):
    """A mutation to leave a group"""
    class Arguments:
        group_copy_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_copy_id):
        group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        member_id = group_copy.member.id
        node_id = Node.to_global_id('GroupMemberType', member_id)
        user_group = group_copy.member.user_group
        group_member = user_group.members.get(member=info.context.user)
        group_member.delete()
        user_group.members_count -= 1
        user_group.save()
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            ModelSignal.send(on_member_removed, member_copy=group_member_copy, member_id=node_id, username=group_member_copy.member.member.username, left=True, sender=GroupMember)
        return LeaveGroup(success=True)

class RemoveGroup(graphene.Mutation):
    """A mutation to remove a group permanently"""
    class Arguments:
        group_copy_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, group_copy_id):
        user_group_copy: UserGroupMemberCopy = get_node_or_error(info, group_copy_id)
        user_group = user_group_copy.member.user_group
        validate_group_creator(user_group, info.context.user)
        group_id = Node.to_global_id('UserGroupType', user_group.id)
        usernames = [member.member.username for member in user_group.members.all()]
        user_group.delete()
        for username in usernames:
            ModelSignal.send(on_group_removed, username=username, group_id=group_id, sender=UserGroup)
        return RemoveGroup(success=True)

class SetArchiveGroup(graphene.Mutation):
    """A mutation to archive a group"""
    class Arguments:
        group_copy_id = graphene.ID()
        is_archived = graphene.Boolean()
        
    group_copy = graphene.Field(UserGroupMemberCopyType)
    
    @login_required
    def mutate(self, info, group_copy_id, is_archived):
        user_group_copy = get_node_or_error(info, group_copy_id)
        validate_group_copy_member(user_group_copy, info.context.user)
        user_group_copy.is_archived = is_archived
        user_group_copy.save()
        return SetArchiveGroup(group_copy=user_group_copy)

class GroupMutations(graphene.ObjectType):
    create_group = CreateGroup.Field()
    create_group_message = CreateGroupMessage.Field()
    create_group_member = CreateGroupMember.Field()
    change_admin = ChangeAdmin.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()
    update_group_message = UpdateGroupMessage.Field()
    delete_group_message = DeleteGroupMessage.Field()
    unsend_group_message = UnsendGroupMessage.Field()
    remove_group_member = RemoveGroupMember.Field()
    leave_group = LeaveGroup.Field()
    remove_group_permanently = RemoveGroup.Field()
    set_archive_group = SetArchiveGroup.Field()
