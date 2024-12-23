from django.shortcuts import get_object_or_404
from .types import CustomUser, GroupMember, Message, UserGroupMemberCopy
from .validators import validate_message_content
import bleach
from graphene.relay.node import Node

def create_group_member(user_group, member_id, info, is_admin=False):
    member: CustomUser = Node.get_node_from_global_id(info, member_id)
    group_member = GroupMember.objects.create(user_group=user_group, member=member, is_admin=is_admin)
    user_group.members_count += 1
    user_group_member_copy = UserGroupMemberCopy.objects.create(member=group_member)
    group_member.save()
    user_group.save()
    user_group_member_copy.save()
    return group_member


def create_message(sender_id, content):
    sender = get_object_or_404(CustomUser, pk=sender_id)
    content = bleach.clean(content)
    validate_message_content(content)
    message = Message.objects.create(sender=sender, content=content)
    message.save()
    return message

def get_node_or_error(info, node_id):
    node = Node.get_node_from_global_id(info, node_id)
    if not node:
        raise ValueError(f"Could not resolve to a node with the global id of '{node_id}'")
    return node
