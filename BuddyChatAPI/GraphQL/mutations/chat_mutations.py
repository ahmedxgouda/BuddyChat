import graphene
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ..validators import validate_chat_user, validate_update_chat_message, validate_delete_chat_message, validate_unsend_chat_message
from ..helpers import create_message
from ...models import Chat, ChatMessage, Notification, CustomUser
from ..types import ChatType, ChatMessageType
import bleach
from django.utils import timezone

class CreateChat(graphene.Mutation):
    
    class Arguments:
        other_user_id = graphene.Int()

    chat = graphene.Field(ChatType)
    other_chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, other_user_id):
        user = info.context.user
        other_user = get_object_or_404(CustomUser, pk=other_user_id)
        chat = Chat.objects.create(user=user, other_user=other_user)
        chat.save()
        other_user_chat = Chat.objects.create(user=other_user, other_user=user)
        other_user_chat.save()
        return CreateChat(chat=chat, other_chat=other_user_chat)

class CreateChatMessage(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_id, content):
        chat = get_object_or_404(Chat, pk=chat_id)
        sender_id = info.context.user.id
        receiver = chat.other_user
        receiver_chat = Chat.objects.get(user=receiver, other_user=info.context.user)
        message = create_message(sender_id, content)
        chat_message = ChatMessage.objects.create(chat=chat, message=message)
        receiver_chat_message = ChatMessage.objects.create(chat=receiver_chat, message=message)
        chat_message.save()
        receiver_chat_message.save()
        chat.last_message = chat_message
        receiver_chat.last_message = receiver_chat_message
        chat.save()
        receiver_chat.save()
        notification = Notification.objects.create(receiver=receiver, message=message)
        notification.save()
        return CreateChatMessage(chat_message=chat_message)
    
class DeleteChat(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        
    chat_id = graphene.Int()
    
    @login_required
    def mutate(self, info, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        validate_chat_user(chat, info.context.user)
        for chat_message in chat.chat_messages.all():
            chat_message.delete()
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
        return UpdateChatMessage(chat_message=chat_message)

class SetChatMessageAsRead(graphene.Mutation):
    
    class Arguments:
        chat_message_id = graphene.Int()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, pk=chat_message_id)
        chat_message.message.read_at = timezone.now()
        chat_message.message.save()
        return SetChatMessageAsRead(chat_message=chat_message)

class UnsendChatMessage(graphene.Mutation):
    class Arguments:
        chat_message_id = graphene.Int()
        
    chat_message_id = graphene.Int()
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, pk=chat_message_id)
        validate_unsend_chat_message(chat_message, info.context.user.id)
        chat = chat_message.chat
        other_user_chat = Chat.objects.get(user=chat.other_user, other_user=info.context.user)
        message = chat_message.message
        last_message_id = chat.last_message.id
        chat_message_id = chat_message.id
        other_user_chat_message = ChatMessage.objects.get(chat=other_user_chat, message=message)
        other_user_chat_message_id = other_user_chat_message.id
        other_user_chat_last_message_id = other_user_chat.last_message.id
        message.delete()
        
        # If the message being deleted is the last message in the chat, update the last_message field of the chat
        if last_message_id == chat_message_id:
            last_message = chat.chat_messages.order_by('-message__date').first()
            chat.last_message = last_message
            chat.save()
            
        # If the message being deleted is the last message in the other user's chat, update the last_message field of the other user's chat
        if other_user_chat_last_message_id == other_user_chat_message_id:
            last_message = other_user_chat.chat_messages.order_by('-message__date').first()
            other_user_chat.last_message = last_message
            other_user_chat.save()
        
        return UnsendChatMessage(chat_message_id=chat_message_id)

class DeleteChatMessage(graphene.Mutation):
    class Arguments:
        chat_message_id = graphene.Int()
        
    chat_message_id = graphene.Int()
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, pk=chat_message_id)
        validate_delete_chat_message(chat_message, info.context.user.id)
        chat = chat_message.chat
        last_message_id = chat.last_message.id
        chat_message_id = chat_message.id
        chat_message.delete()
        
        # If the message being deleted is the last message in the chat, update the last_message field of the chat
        if last_message_id == chat_message_id:
            last_message = chat.chat_messages.order_by('-message__date').first()
            chat.last_message = last_message
            chat.save()
        
        return DeleteChatMessage(chat_message_id=chat_message_id)

class SetChatArchived(graphene.Mutation):
    class Arguments:
        chat_id = graphene.Int()
        archived = graphene.Boolean()
        
    chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, chat_id, archived):
        chat = get_object_or_404(Chat, pk=chat_id)
        validate_chat_user(chat, info.context.user)
        chat.archived = archived
        chat.save()
        return SetChatArchived(chat=chat)

class ChatMutations(graphene.ObjectType):
    create_chat = CreateChat.Field()
    create_chat_message = CreateChatMessage.Field()
    delete_chat = DeleteChat.Field()
    update_chat_message = UpdateChatMessage.Field()
    unsend_chat_message = UnsendChatMessage.Field()
    delete_chat_message = DeleteChatMessage.Field()
    set_chat_message_as_read = SetChatMessageAsRead.Field()
    set_chat_archived = SetChatArchived.Field()
