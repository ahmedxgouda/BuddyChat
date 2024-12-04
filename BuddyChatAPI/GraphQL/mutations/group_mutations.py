import graphene
import bleach
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ..validators import validate_group_title, validate_group_message_sender, validate_admin, validate_message_content
from ..helpers import create_group_member, create_message
from ...models import UserGroup, GroupMember, GroupMessage, Notification, CustomUser
from ..types import UserGroupType, GroupMemberType, GroupMessageType

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

class GroupMutations(graphene.ObjectType):
    create_group = CreateGroup.Field()
    create_group_message = CreateGroupMessage.Field()
    create_group_member = CreateGroupMember.Field()
    assign_admin = AssignAdmin.Field()
    