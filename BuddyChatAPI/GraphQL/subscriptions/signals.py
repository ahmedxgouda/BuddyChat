from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from ...models import ChatMessage

@receiver(post_save, sender=ChatMessage)
async def chat_message_created(sender, instance, created, **kwargs):
    print('Chat message created')
    if created:
        channel_layer = get_channel_layer()
        group_name = f'user_{instance.chat.user.username}'
        message = instance
        await channel_layer.group_send(
            group_name,
            {
                'type': 'chat.message',
                'message': message
            }
        )
    print('Message sent')
    print(f'From signal: {group_name}')
