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

# Helper function to define the operation, message_holder, message_type, chat_type, and chat_id based on the chat type
def define_variables(is_chat, instance, operation_suffix, is_deleted_chat=False) -> tuple[str, str, str, str, int, str]:
    if is_deleted_chat:
        operation = f'CHAT_{operation_suffix}'
        message_holder = None
        message_type = None
        chat_type = 'ChatType' if is_chat else 'UserGroupMemberCopyType'
        chat_key = 'chat' if is_chat else 'groupCopy'
        chat_id = instance.id
    else:
        operation, message_holder, message_type, chat_type, chat_id, chat_key = define_message_variables(is_chat, instance, operation_suffix)
        
    return operation, message_holder, message_type, chat_type, chat_id, chat_key

def define_message_variables(is_chat, instance, operation_suffix, message_id=None) -> tuple[str, str, str, str, int, str]:
    if is_chat:
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
def broadcast_message(sender, instance, is_chat, operation_suffix, add_message_details=False, **kwargs):
    operation, message_holder, message_type, chat_type, chat_id, chat_key = define_variables(is_chat, instance, operation_suffix)
    channel_layer = get_channel_layer()
    if add_message_details:
        message = {
            'id': Node.to_global_id('MessageType', instance.message.id),
            'content': instance.message.content,
            'sender': {
                'id': Node.to_global_id('CustomUserType', instance.message.sender.id)
            }
        }
    else:
        message = None
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.chat.user.username}',
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
def broadcast_created_message(sender, instance, is_chat, **kwargs):
    broadcast_message(sender, instance, is_chat, 'CREATED', add_message_details=True)
    
@receiver(on_message_updated)
def broadcast_updated_message(sender, instance, is_chat, **kwargs):
    broadcast_message(sender, instance, is_chat, 'UPDATED', add_message_details=True)
    
@receiver(on_message_unsent)
def broadcast_unsent_message(sender, instance, is_chat, **kwargs):
    broadcast_message(sender, instance, is_chat, 'UNSENT')

@receiver(on_message_deleted)
def broadcast_deleted_message(sender, message_id, is_chat, chat_id, username, **kwargs):
    # TODO: Fix this function to broadcast the deleted message
    operation, message_holder, message_type, chat_type, _, chat_key = define_message_variables(is_chat, None, 'DELETED', message_id)
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
def broadcast_read_message(sender, instance, is_chat, **kwargs):
    broadcast_message(sender, instance, is_chat, 'READ')

@receiver(on_notification_created)
def broadcast_created_notification(sender, instance, **kwargs):
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
def broadcast_deleted_chat(sender, instance, is_chat, **kwargs):
    operation, message_holder, message_type, chat_type, chat_id, chat_key = define_variables(is_chat, instance, 'DELETED', is_deleted_chat=True)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.user.username}',
        {
            'type': 'broadcast',
            'operation': operation,
            chat_key: {
                'id': Node.to_global_id(chat_type, chat_id),
            }
        }
    )
