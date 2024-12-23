from django.db.models.signals import ModelSignal
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from graphene.relay import Node

on_message_created = ModelSignal(use_caching=True)
on_message_updated = ModelSignal(use_caching=True)
on_message_deleted = ModelSignal(use_caching=True)
on_message_unsent = ModelSignal(use_caching=True)
on_notification_created = ModelSignal(use_caching=True)
on_message_read = ModelSignal(use_caching=True)
on_chat_deleted = ModelSignal(use_caching=True)
on_group_updated = ModelSignal(use_caching=True)
on_group_removed = ModelSignal(use_caching=True)
on_member_added = ModelSignal(use_caching=True)
on_member_removed = ModelSignal(use_caching=True)

# Helper function to define the operation, message_holder, message_type, chat_type, and chat_id based on the chat type
def define_variables(instance, operation_suffix, is_chat=False, is_message=False) -> tuple[str, str, str, str, int, str]:
    if not is_message:
        operation = f'CHAT_{operation_suffix}' if is_chat else f'GROUP_{operation_suffix}'
        message_holder = None
        message_type = None
        chat_type = 'ChatType' if is_chat else 'UserGroupMemberCopyType'
        chat_key = 'chat' if is_chat else 'groupCopy'
        chat_id = instance.id
    else:
        operation, message_holder, message_type, chat_type, chat_id, chat_key = define_message_variables(is_chat, instance, operation_suffix)
        
    return operation, message_holder, message_type, chat_type, chat_id, chat_key

def define_message_variables(is_chat_message, instance, operation_suffix) -> tuple[str, str, str, str, int, str]:
    chat_id = None
    if is_chat_message:
        operation = f'CHAT_MESSAGE_{operation_suffix}'
        message_holder = 'chatMessage'
        message_type = 'ChatMessageType'
        chat_type = 'ChatType'
        chat_key = 'chat'
        if instance:
            chat_id = instance.chat.id
    else:
        operation = f'GROUP_MESSAGE_{operation_suffix}'
        message_holder = 'groupMessage'
        message_type = 'GroupMessageType'
        chat_type = 'UserGroupMemberCopyType'
        chat_key = 'groupCopy'
        if instance:
            chat_id = instance.user_group_copy.id        
    return operation, message_holder, message_type, chat_type, chat_id, chat_key

# A generic function to broadcast a message eihther created, updated
def broadcast_message(instance, is_chat, operation_suffix, add_message_details=False, **kwargs):
    operation, message_holder, message_type, chat_type, chat_id, chat_key = define_variables(instance, operation_suffix, is_chat, is_message=True)
    channel_layer = get_channel_layer()
    if add_message_details:
        message = {
            'id': Node.to_global_id('MessageType', instance.message.id),
            'content': instance.message.content,
            'date': instance.message.date.isoformat(),
            'sender': {
                'id': Node.to_global_id('CustomUserType', instance.message.sender.id)
            }
        }
    else:
        message = None
    if is_chat:
        username = instance.chat.user.username
    else:
        username = instance.user_group_copy.member.member.username
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': operation,
            message_holder: {
                'id': Node.to_global_id(message_type, instance.id),
                'message': message,
                chat_key: {
                    'id': Node.to_global_id(chat_type, chat_id),
                }
            }
        }
    )

@receiver(on_message_created)
def broadcast_created_message(instance, is_chat, **kwargs):
    broadcast_message(instance, is_chat, 'CREATED', add_message_details=True)
    
@receiver(on_message_updated)
def broadcast_updated_message(instance, is_chat, **kwargs):
    broadcast_message(instance, is_chat, 'UPDATED', add_message_details=True)
    
@receiver(on_message_unsent)
def broadcast_unsent_message(instance, is_chat, **kwargs):
    broadcast_message(instance, is_chat, 'UNSENT')

@receiver(on_message_deleted)
def broadcast_deleted_message(message_id, is_chat, chat_id, username, **kwargs):
    operation, message_holder, message_type, chat_type, _, chat_key = define_message_variables(is_chat, None, 'DELETED')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': operation,
            message_holder: {
                'id': Node.to_global_id(message_type, message_id),
                chat_key: {
                    'id': Node.to_global_id(chat_type, chat_id),
                }
            }
        }
    )
    
@receiver(on_message_read)
def broadcast_read_message(instance, is_chat, **kwargs):
    broadcast_message(instance, is_chat, 'READ')

@receiver(on_notification_created)
def broadcast_created_notification(instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.receiver.username}',
        {
            'type': 'broadcast',
            'operation': 'NOTIFICATION_CREATED',
            'notification': {
                'id': Node.to_global_id('NotificationType', instance.id),
                'message': {
                    'id': Node.to_global_id('MessageType', instance.message.id),
                    'content': instance.message.content,
                    'sender': {
                        'id': Node.to_global_id('CustomUserType', instance.message.sender.id)
                    }
                }
            }
        }
    )
    
@receiver(on_chat_deleted)
def broadcast_deleted_chat(instance, is_chat, **kwargs):
    operation, message_holder, message_type, chat_type, chat_id, chat_key = define_variables(instance, 'DELETED', is_chat)
    channel_layer = get_channel_layer()
    username = instance.user.username if is_chat else instance.member.member.username
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': operation,
            chat_key: {
                'id': Node.to_global_id(chat_type, chat_id),
            }
        }
    )

@receiver(on_group_updated)
def broadcast_updated_group(instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.member.member.username}',
        {
            'type': 'broadcast',
            'operation': 'GROUP_UPDATED',
            'groupCopy': {
                'id': Node.to_global_id('UserGroupMemberCopyType', instance.id),
                'group': {
                    'id': Node.to_global_id('UserGroupType', instance.member.user_group.id),
                    'title': instance.member.user_group.title,
                    'description': instance.member.user_group.description,
                    'groupImage': instance.member.user_group.group_image.url,
                }
            }
        }
    )
    
@receiver(on_group_removed)
def broadcast_removed_group(username, group_id, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': 'GROUP_PERMANENTLY_REMOVED',
            'groupId': group_id
        }
    )
    
@receiver(on_member_added)
def broadcast_added_member(member_copy, new_member, username, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': 'MEMBER_ADDED',
            'groupCopy': {
                'id': Node.to_global_id('UserGroupMemberCopyType', member_copy.id),
                'member': {
                    'id': Node.to_global_id('GroupMemberType', new_member.id),
                    'joinedAt': new_member.joined_at.isoformat(),
                    'group_id': Node.to_global_id('UserGroupType', new_member.user_group.id),
                    'user': {
                        'id': Node.to_global_id('CustomUserType', new_member.member.id),
                        'username': new_member.member.username
                    },
                }
            }
        }
    )
    
@receiver(on_member_removed)
def broadcast_removed_member(member_copy, member_id, username, removed_by_id=None, left=False, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{username}',
        {
            'type': 'broadcast',
            'operation': 'MEMBER_LEFT' if left else 'MEMBER_REMOVED',
            'groupCopy': {
                'id': Node.to_global_id('UserGroupMemberCopyType', member_copy.id),
                'member_id': member_id,
            },
            'removedById': Node.to_global_id('CustomUserType', removed_by_id) if removed_by_id else None
        }
    )