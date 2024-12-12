import graphene
import bleach
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ..validators import validate_group_title, validate_group_message_sender, validate_admin, validate_message_content, validate_group_description, validate_group_message_member
from ..helpers import create_group_member, create_message
from ...models import UserGroup, GroupMember, GroupMessage, Notification, CustomUser, UserGroupMemberCopy
from ..types import UserGroupType, GroupMemberType, GroupMessageType
from django.utils import timezone

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
        user_group.members_count = 1
        create_group_member(user_group, created_by_id, is_admin=True)
        return CreateGroup(user_group=user_group)
    
class CreateGroupMessage(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    @login_required
    def mutate(self, info, user_group_id, content):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        group_member = user_group.members.get(member=info.context.user)
        sender_id = info.context.user.id
        
        # check if the sender is a member of the group
        validate_group_message_member(group_member)
        content = bleach.clean(content)
        validate_message_content(content)
        message = create_message(sender_id, content)
        
        # Create group message for each group member - for deleting and unsending messages
        for group_member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=group_member)
            group_message = GroupMessage.objects.create(message=message, user_group_copy=group_member_copy)
            group_message.save()
            group_member_copy.last_message = group_message
            group_member_copy.save()
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
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        group_member = create_group_member(user_group, member_id)
        return CreateGroupMember(group_member=group_member)

class ChangeAdmin(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        member_id = graphene.Int()
        is_admin = graphene.Boolean()
        
    group_member = graphene.Field(GroupMemberType)
    
    @login_required
    def mutate(self, info, user_group_id, member_id, is_admin):
        group_member = get_object_or_404(GroupMember, user_group_id=user_group_id, member_id=member_id)
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        group_member.is_admin = is_admin
        group_member.save()
        return ChangeAdmin(group_member=group_member)
    
class UpdateGroup(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        group_image = graphene.String(required=False)
        
    user_group = graphene.Field(UserGroupType)
    
    @login_required
    def mutate(self, info, user_group_id, title, description, group_image):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
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
        return UpdateGroup(user_group=user_group)

class DeleteGroup(graphene.Mutation):
    class Arguments:
        user_group_copy_id = graphene.Int()
        
    user_group_copy_id = graphene.Int()
    
    @login_required
    def mutate(self, info, user_group_copy_id):
        user_group_copy = get_object_or_404(UserGroupMemberCopy, pk=user_group_copy_id)
        for group_message in user_group_copy.group_messages.all():
            group_message.delete()
        return DeleteGroup(user_group_copy_id=user_group_copy_id)

class UpdateGroupMessage(graphene.Mutation):
    class Arguments:
        group_message_id = graphene.Int()
        content = graphene.String()
        
    group_message = graphene.Field(GroupMessageType)
    
    @login_required
    def mutate(self, info, group_message_id, content):
        group_message = get_object_or_404(GroupMessage, pk=group_message_id)
        group_member = group_message.user_group_copy.member
        validate_group_message_sender(group_member, group_message)
        content = bleach.clean(content)
        validate_message_content(content)
        group_message.message.content = content
        group_message.message.save()
        return UpdateGroupMessage(group_message=group_message)

class DeleteGroupMessage(graphene.Mutation):
    class Arguments:
        group_message_id = graphene.Int()
        
    group_message_id = graphene.Int()
    
    @login_required
    def mutate(self, info, group_message_id):
        group_message = get_object_or_404(GroupMessage, pk=group_message_id)
        last_message_id = group_message.user_group_copy.last_message.id
        group_message.delete()
        if last_message_id == group_message.id:
            group_message.user_group_copy.last_message = group_message.user_group_copy.group_messages.first()
            group_message.user_group_copy.save()
        return DeleteGroupMessage(group_message_id=group_message_id)

class UnsendGroupMessage(graphene.Mutation):
    class Arguments:
        group_message_id = graphene.Int()
        
    group_message_id = graphene.Int()
    
    @login_required
    def mutate(self, info, group_message_id):
        group_message = get_object_or_404(GroupMessage, pk=group_message_id)
        group_member = group_message.user_group_copy.member
        validate_group_message_sender(group_member, group_message)
        last_message_id = group_message.user_group_copy.last_message.message.id
        user_group = group_message.user_group_copy.member.user_group
        
        # Update last message for all group members
        for member in user_group.members.all():
            group_member_copy = UserGroupMemberCopy.objects.get(member=member)
            if last_message_id == group_member_copy.last_message.message.id:
                group_member_copy.last_message = group_member_copy.group_messages.first()
                group_member_copy.save()
                
        group_message.message.delete()
        return UnsendGroupMessage(group_message_id=group_message_id)
    
class RemoveGroupMember(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        member_id = graphene.Int()
        
    group_member_id = graphene.Int()
    
    @login_required
    def mutate(self, info, user_group_id, member_id):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        admin_member = user_group.members.get(member=info.context.user)
        validate_admin(user_group, admin_member)
        group_member = get_object_or_404(GroupMember, user_group_id=user_group_id, member_id=member_id)
        group_member.delete()
        return RemoveGroupMember(group_member=group_member)

class LeaveGroup(graphene.Mutation):
    class Arguments:
        user_group_id = graphene.Int()
        
    group_member_id = graphene.Int()
    
    @login_required
    def mutate(self, info, user_group_id):
        user_group = get_object_or_404(UserGroup, pk=user_group_id)
        group_member = user_group.members.get(member=info.context.user)
        group_member.delete()
        return LeaveGroup(group_member=group_member)


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
    