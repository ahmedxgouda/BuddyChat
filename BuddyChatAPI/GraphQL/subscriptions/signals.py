from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ...models import ChatMessage


@receiver(post_save, sender=ChatMessage)
def chat_message_created(sender, instance, created, **kwargs):
    print('Chat message created')
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.chat.user.username}",
            {
                'type': 'send.update',
                'data': instance.id
            }
        )
