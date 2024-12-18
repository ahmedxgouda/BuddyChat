from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ...models import ChatMessage, Chat, Notification, UserGroupMemberCopy, GroupMessage

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
        
# @receiver(post_save, sender=GroupMessage)
# def group_message_created(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"group_{instance.group.id}",
#             {
#                 'type': 'send_update',
#                 'data': {
#                     'type': 'group_message',
#                     'group_message': {
#                         'id': instance.id,
#                         'group': instance.group.id,
#                         'message': {
#                             'id': instance.message.id,
#                             'content': instance.message.content,
#                         }
#                     }
#                 }
#             }
#         )