import graphene
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ..validators import validate_chat_users, validate_chat_message, validate_delete_chat, validate_update_chat_message, validate_delete_chat_message
from ..helpers import create_message
from ...models import Chat, ChatMessage, CustomUser, Notification
from ..types import ChatType, ChatMessageType
import bleach

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
    
class DeleteChat(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        
    chat_id = graphene.Int()
    
    @login_required
    def mutate(self, info, chat_id):
        validate_delete_chat(chat_id, info.context.user)
        chat = get_object_or_404(Chat, pk=chat_id)
        chat.delete()
        return DeleteChat(chat_id=chat_id)
    
class UpdateChatMessage(graphene.Mutation):
    class Arguments:
        chat_message_id = graphene.Int()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_message_id, content):
        chat_message = get_object_or_404(ChatMessage, pk=chat_message_id)
        validate_update_chat_message(chat_message, info.context.user.id)
        chat_message.message.content = bleach.clean(content)
        chat_message.message.save()
        chat_message.save()
        return UpdateChatMessage(chat_message=chat_message)

class DeleteChatMessage(graphene.Mutation):
    class Arguments:
        chat_message_id = graphene.Int()
        
    chat_message_id = graphene.Int()
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, pk=chat_message_id)
        validate_delete_chat_message(chat_message, info.context.user.id)
        
        # If the message being deleted is the last message in the chat, update the last_message field of the chat
        if chat_message.chat.last_message.id == chat_message.id:
            if chat_message.chat.chat_messages.count() == 1:
                chat_message.chat.last_message = None
            else:
                last_message = chat_message.chat.chat_messages.order_by('-message__date').first()
                chat_message.chat.last_message = last_message
            chat_message.chat.save()
        chat_message.message.delete()
        return DeleteChatMessage(chat_message_id=chat_message_id)

class ChatMutations(graphene.ObjectType):
    create_chat = CreateChat.Field()
    create_chat_message = CreateChatMessage.Field()
    delete_chat = DeleteChat.Field()
    update_chat_message = UpdateChatMessage.Field()
    delete_chat_message = DeleteChatMessage.Field()
