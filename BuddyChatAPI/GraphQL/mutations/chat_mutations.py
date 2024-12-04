import graphene
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ..validators import validate_chat_users, validate_chat_message
from ..helpers import create_message
from ...models import Chat, ChatMessage, CustomUser, Notification
from ..types import ChatType, ChatMessageType

class CreateChat(graphene.Mutation):
    class Arguments:
        user1_id = graphene.Int()
        user2_id = graphene.Int()
        
    chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, user1_id, user2_id):
        user1 = get_object_or_404(CustomUser, pk=user1_id)
        user2 = get_object_or_404(CustomUser, pk=user2_id)
        validate_chat_users(user1, user2)
        chat = Chat.objects.create(user1=user1, user2=user2)
        chat.save()
        return CreateChat(chat=chat)
    
class CreateChatMessage(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_id, content):
        chat = get_object_or_404(Chat, pk=chat_id)
        sender_id = info.context.user.id
        validate_chat_message(chat, sender_id)
        message = create_message(sender_id, content)
        chat_message = ChatMessage.objects.create(chat=chat, message=message)
        chat_message.save()
        chat.last_message = chat_message
        chat.save()
        receiver = chat.user1 if chat.user1_id != sender_id else chat.user2
        notification = Notification.objects.create(receiver=receiver, message=message)
        notification.save()
        return CreateChatMessage(chat_message=chat_message)
    
class ChatMutations(graphene.ObjectType):
    create_chat = CreateChat.Field()
    create_chat_message = CreateChatMessage.Field()
