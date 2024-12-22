from django.db.models.signals import ModelSignal
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

signal = ModelSignal(use_caching=True)

@receiver(signal)
def broadcast(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{instance.chat.user.username}',
        {
            'type': 'broadcast',
            'payload': {
                'chat_message': {
                    'id': instance.id,
                    'message': {
                        'id': instance.message.id,
                        'content': instance.message.content,
                        'sender': {
                            'id': instance.message.sender.id,
                            'username': instance.message.sender.username,
                            'first_name': instance.message.sender.first_name,
                            'last_name': instance.message.sender.last_name
                        }
                    }
                },
                'chat': {
                    'id': instance.chat.id,
                    'user': {
                        'id': instance.chat.user.id,
                        'username': instance.chat.user.username,
                        'first_name': instance.chat.user.first_name,
                        'last_name': instance.chat.user.last_name
                    },
                    'other_user': {
                        'id': instance.chat.other_user.id,
                        'username': instance.chat.other_user.username,
                        'first_name': instance.chat.other_user.first_name,
                        'last_name': instance.chat.other_user.last_name
                    }
                }
            }
        }
    )