from django.shortcuts import get_object_or_404
from .types import CustomUser, GroupMember, Message, UserGroupMemberCopy
from .validators import validate_group_member, validate_message_content
import bleach

def create_group_member(user_group, member_id, is_admin=False):
    member = get_object_or_404(CustomUser, pk=member_id)
    validate_group_member(user_group, member)
    group_member = GroupMember.objects.create(user_group=user_group, member=member, is_admin=is_admin)
    group_member.save()
    user_group.members_count += 1
    user_group.save()
    user_group_member_copy = UserGroupMemberCopy.objects.create(member=member)
    user_group_member_copy.save()
    return group_member

def create_message(sender_id, content):
    sender = get_object_or_404(CustomUser, pk=sender_id)
    content = bleach.clean(content)
    validate_message_content(content)
    message = Message.objects.create(sender=sender, content=content)
    message.save()
    return message

