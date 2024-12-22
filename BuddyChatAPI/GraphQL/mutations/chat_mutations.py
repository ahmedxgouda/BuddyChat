import graphene
from graphql_jwt.decorators import login_required
from ..validators import validate_chat_user, validate_update_chat_message, validate_delete_chat_message, validate_unsend_chat_message, validate_chat_member
from ..helpers import create_message
from ...models import Chat, ChatMessage, Notification
from ..types import ChatType, ChatMessageType
import bleach
from django.utils import timezone
from graphene.relay.node import Node
from ..subscriptions.signals import signal
from django.db.models.signals import ModelSignal

class CreateChat(graphene.Mutation):
    """A mutation to create a chat for each user"""
    
    class Arguments:
        other_user_id = graphene.ID()

    chat = graphene.Field(ChatType)
    other_chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, other_user_id):
        user = info.context.user
        other_user = Node.get_node_from_global_id(info, other_user_id)
        chat = Chat.objects.create(user=user, other_user=other_user)
        chat.save()
        other_user_chat = Chat.objects.create(user=other_user, other_user=user)
        other_user_chat.save()
        return CreateChat(chat=chat, other_chat=other_user_chat)
    
class CreateSelfChat(graphene.Mutation):
    """A mutation to create a chat with oneself"""
        
    chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info):
        user = info.context.user
        chat = Chat.objects.create(user=user, other_user=user)
        chat.save()
        return CreateSelfChat(chat=chat)

class CreateChatMessage(graphene.Mutation):
    """A mutation to create two chat messages, one for each user in each chat"""
    class Arguments:
        chat_id = graphene.ID()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_id, content):
        chat: Chat = Node.get_node_from_global_id(info, chat_id)
        sender_id = info.context.user.id
        validate_chat_member(chat, sender_id)
        message = create_message(sender_id, content)
        chat_message = ChatMessage.objects.create(chat=chat, message=message)
        chat_message.save()
        chat.last_message = chat_message
        chat.save()
        
        receiver = chat.other_user
        notification = Notification.objects.create(receiver=receiver, message=message)
        notification.save()
        
        # If the chat is a self chat, return the chat message
        if receiver.id == sender_id:
            return CreateChatMessage(chat_message=chat_message)
        
        receiver_chat = Chat.objects.get(user=receiver, other_user=info.context.user)
        receiver_chat_message = ChatMessage.objects.create(chat=receiver_chat, message=message)
        receiver_chat_message.save()
        receiver_chat.last_message = receiver_chat_message
        receiver_chat.save()
        ModelSignal.send(signal, sender=ChatMessage, instance=receiver_chat_message, created=True)
        return CreateChatMessage(chat_message=chat_message)
    
class DeleteChat(graphene.Mutation):
    """A mutation to delete a chat"""
    class Arguments:
        chat_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, chat_id):
        chat: Chat = Node.get_node_from_global_id(info, chat_id)
        validate_chat_user(chat, info.context.user)
        for chat_message in chat.chat_messages.all():
            chat_message.delete()
        return DeleteChat(success=True)
    
class UpdateChatMessage(graphene.Mutation):
    """A mutation to update a chat message"""
    class Arguments:
        chat_message_id = graphene.ID()
        content = graphene.String()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_message_id, content):
        chat_message: ChatMessage = Node.get_node_from_global_id(info, chat_message_id)
        validate_update_chat_message(chat_message, info.context.user.id)
        chat_message.message.content = bleach.clean(content)
        chat_message.message.save()
        return UpdateChatMessage(chat_message=chat_message)

class SetChatMessageAsRead(graphene.Mutation):
    """A mutation to set a chat message as read"""
    class Arguments:
        chat_message_id = graphene.ID()
        
    chat_message = graphene.Field(ChatMessageType)
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message: ChatMessage = Node.get_node_from_global_id(info, chat_message_id)
        chat_message.message.read_at = timezone.now()
        chat_message.message.save()
        return SetChatMessageAsRead(chat_message=chat_message)

class UnsendChatMessage(graphene.Mutation):
    """A mutation to unsend a chat message. Unsend means to delete the message from the two chats"""
    class Arguments:
        chat_message_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message: ChatMessage = Node.get_node_from_global_id(info, chat_message_id)
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
            
        # If the chat is a self chat then no need to update the last message of the other user's chat
        if chat.user.id == chat.other_user.id:
            return UnsendChatMessage(success=True)
        
        # If the message being deleted is the last message in the other user's chat, update the last_message field of the other user's chat
        if other_user_chat_last_message_id == other_user_chat_message_id:
            last_message = other_user_chat.chat_messages.order_by('-message__date').first()
            other_user_chat.last_message = last_message
            other_user_chat.save()
        
        return UnsendChatMessage(success=True)

class DeleteChatMessage(graphene.Mutation):
    """A mutation to delete a chat message. Delete means to delete the message from the user's chat only"""
    class Arguments:
        chat_message_id = graphene.ID()
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, chat_message_id):
        chat_message = Node.get_node_from_global_id(info, chat_message_id)
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
        
        return DeleteChatMessage(success=True)

class SetChatArchived(graphene.Mutation):
    """A mutation to set a chat as archived or unarchived"""
    class Arguments:
        chat_id = graphene.ID()
        archived = graphene.Boolean()
        
    chat = graphene.Field(ChatType)
    
    @login_required
    def mutate(self, info, chat_id, archived):
        chat = Node.get_node_from_global_id(info, chat_id)
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
    create_self_chat = CreateSelfChat.Field()
