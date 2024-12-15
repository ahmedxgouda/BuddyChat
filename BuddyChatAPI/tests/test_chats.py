from graphene_django.utils.testing import GraphQLTestCase
from ..models import Chat, CustomUser, ChatMessage, Message, Notification
from graphene.relay import Node
class ChatTestCase(GraphQLTestCase):
    def setUp(self):
        # Prepare the users
        self.user1 = CustomUser.objects.create_user(username='test', first_name='test', last_name='test', password="123456789Test", email="a@g.com", phone="+201234567890")
        self.user2 = CustomUser.objects.create_user(username='test1', first_name='test1', last_name='test1', password="113456789Test", email="a@d.com", phone="+201234567891")
        self.user3 = CustomUser.objects.create_user(username='test2', first_name='test2', last_name='test2', password="113456789Test", email="b@f.com", phone="+201234567892")
        self.user4 = CustomUser.objects.create_user(username='test3', first_name='test3', last_name='test3', password="113456789Test", email="a@a.com", phone="+201234567893")
        self.user1.save()
        self.user2.save()
        self.user3.save()
        self.user4.save()
        # Create chats
        self.chat1 = Chat.objects.create(user=self.user1, other_user=self.user2)
        self.chat2 = Chat.objects.create(user=self.user1, other_user=self.user3)
        self.chat3 = Chat.objects.create(user=self.user2, other_user=self.user4)
        self.chat4 = Chat.objects.create(user=self.user2, other_user=self.user1)
        self.chat5 = Chat.objects.create(user=self.user3, other_user=self.user1)
        self.chat6 = Chat.objects.create(user=self.user4, other_user=self.user2)
        
        self.chat1.save()
        self.chat2.save()
        self.chat3.save()
        self.chat4.save()
        self.chat5.save()
        self.chat6.save()
        # Create messages and chat messages
        self.message1 = Message.objects.create(sender=self.user1, content='Hello')
        self.message2 = Message.objects.create(sender=self.user1, content='Hello')
        self.message3 = Message.objects.create(sender=self.user2, content='Hello')
        self.message4 = Message.objects.create(sender=self.user2, content='Hello')
        self.message1.save()
        self.message2.save()
        self.message3.save()
        self.message4.save()

        self.chat_message1 = ChatMessage.objects.create(chat=self.chat1, message=self.message1)
        self.chat_message1_other = ChatMessage.objects.create(chat=self.chat4, message=self.message1)
        self.chat_message2 = ChatMessage.objects.create(chat=self.chat2, message=self.message2)
        self.chat_message2_other = ChatMessage.objects.create(chat=self.chat5, message=self.message2)
        self.chat_message3 = ChatMessage.objects.create(chat=self.chat3, message=self.message3)
        self.chat_message3_other = ChatMessage.objects.create(chat=self.chat6, message=self.message3)
        self.chat_message4 = ChatMessage.objects.create(chat=self.chat3, message=self.message4)
        self.chat_message4_other = ChatMessage.objects.create(chat=self.chat6, message=self.message4)
        
        self.chat_message1.save()
        self.chat_message2.save()
        self.chat_message3.save()
        self.chat_message4.save()
        self.chat_message1_other.save()
        self.chat_message2_other.save()
        self.chat_message3_other.save()
        self.chat_message4_other.save()
        
        self.chat1.last_message = self.chat_message1
        self.chat2.last_message = self.chat_message2
        self.chat3.last_message = self.chat_message4
        self.chat4.last_message = self.chat_message1_other
        self.chat5.last_message = self.chat_message2_other
        self.chat6.last_message = self.chat_message4_other

        self.chat1.save()
        self.chat2.save()
        self.chat3.save()
        self.chat4.save()
        self.chat5.save()
        self.chat6.save()
        # Token for authentication
        token_query = '''
            mutation Login($username: String!, $password: String!) {
                login(username: $username, password: $password) {
                    token
                }  
            }              
        '''

        user1_token_response = self.query(
            token_query
            , variables={'username': 'test', 'password': '123456789Test'}
        )
        
        user2_token_response = self.query(
            token_query,
            variables={'username': 'test1', 'password': '113456789Test'}
        )
        
        self.user1_token = user1_token_response.json()['data']['login']['token']
        self.user2_token = user2_token_response.json()['data']['login']['token']
        # Repeated mutation for testing
        self.create_chat_mutation = '''
            mutation CreateChat($otherUserId: ID!) {
                createChat(otherUserId: $otherUserId) {
                    chat {
                        id
                        user {
                            id
                            username
                        }
                        otherUser {
                            id
                            username
                        }
                    }
                }
            }
        '''
        self.create_chat_message_mutation = '''
            mutation CreateChatMessage($chatId: ID!, $content: String!) {
                createChatMessage(chatId: $chatId, content: $content) {
                    chatMessage {
                        id
                        chat {
                            id
                        }
                        message {
                            id
                            sender {
                                id
                                username
                            }
                            content
                        }
                    }
                }
            }
        '''
        self.chat_messages_count = ChatMessage.objects.count()
        self.chat_count = Chat.objects.count()
        
    def test_query_chats(self):
        response = self.query(
            '''
            query {
                chats {
                    edges {
                        node {
                            id
                            user {
                                id
                                username
                            }
                            otherUser {
                                id
                                username
                            }
                        }
                    }
                }
            }
            ''',
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['chats']['edges']), 2)
        self.assertEqual(content['data']['chats']['edges'][0]['node']['user']['username'], 'test')
        
    def test_query_chat(self):
        chat_id = Node.to_global_id('ChatType', self.chat1.id)
        response = self.query(
            '''
            query chat($id: ID!) {
                chat(id: $id) {
                    id
                    user {
                        id
                        username
                    }
                    otherUser {
                        id
                        username
                    }
                }
            }
            ''',
            variables={'id': chat_id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['chat']['user']['username'], 'test')
        
    def test_create_chat(self):
        user_id = Node.to_global_id('CustomUserType', self.user3.id)
        response = self.query(
            self.create_chat_mutation,
            variables={'otherUserId': user_id},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.chat_count += 2
        self.assertEqual(content['data']['createChat']['chat']['user']['username'], 'test1')
        self.assertEqual(content['data']['createChat']['chat']['otherUser']['username'], 'test2')
        
    def test_create_self_chat(self):
        response = self.query(
            '''
            mutation {
                createSelfChat {
                    chat {
                        id
                        user {
                            id
                            username
                        }
                        otherUser {
                            id
                            username
                        }
                    }
                }
            }
            ''',
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.chat_count += 1
        self.assertEqual(content['data']['createSelfChat']['chat']['user']['username'], 'test')
        self.assertEqual(content['data']['createSelfChat']['chat']['otherUser']['username'], 'test')
    
    def test_create_chat_message(self):
        chat_id = Node.to_global_id('ChatType', self.chat1.id)
        response = self.query(
            self.create_chat_message_mutation,
            variables={'chatId': chat_id, 'content': 'Hello'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.chat_messages_count += 2
        self.assertEqual(content['data']['createChatMessage']['chatMessage']['message']['content'], 'Hello')
        self.assertEqual(content['data']['createChatMessage']['chatMessage']['message']['sender']['username'], 'test')
        self.assertEqual(len(ChatMessage.objects.all()), self.chat_messages_count)
        
        # Check if notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.receiver.id, self.user2.id)
        self.assertEqual(notification.message.id, int(content['data']['createChatMessage']['chatMessage']['message']['id']))
        
    def test_create_chat_message_invalid_chat(self):
        chat_id = Node.to_global_id('ChatType', self.chat3.id)
        response = self.query(
            self.create_chat_message_mutation,
            variables={'chatId': chat_id, 'content': 'Hello'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'The user is not a member of this chat')

    def test_delete_chat(self):
        chat1_id = Node.to_global_id('ChatType', self.chat1.id)
        messages_count = self.chat1.chat_messages.count()
        response = self.query(
            '''
            mutation DeleteChat($chatId: ID!) {
                deleteChat(chatId: $chatId) {
                    success
                }
            }
            ''',
            variables={'chatId': chat1_id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteChat']['success'], True)
        self.assertEqual(Chat.objects.count(), self.chat_count)
        self.assertEqual(ChatMessage.objects.count(), self.chat_messages_count - messages_count)
        
    def test_delete_chat_message(self):
        chat_message_id = self.chat_message4.id
        query = '''
            mutation DeleteChatMessage($chatMessageId: Int!) {
                deleteChatMessage(chatMessageId: $chatMessageId) {
                    chatMessageId
                }
            }
        '''
        response = self.query(
            query=query,
            variables={'chatMessageId': self.chat_message4.id},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        
        content = response.json()
        
        self.assertResponseNoErrors(response)
        self.assertEqual(ChatMessage.objects.count(), 3)
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(content['data']['deleteChatMessage']['chatMessageId'], chat_message_id)
        
        response = self.query(
            query=query,
            variables={'chatMessageId': self.chat_message3.id},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        
        content = response.json()
        
        chat_message_id = self.chat_message3.id
        self.assertResponseNoErrors(response)
        self.assertEqual(ChatMessage.objects.count(), 2)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(content['data']['deleteChatMessage']['chatMessageId'], chat_message_id)
        
    def test_update_chat_message(self):
        query = '''
            mutation UpdateChatMessage($chatMessageId: Int!, $content: String!) {
                updateChatMessage(chatMessageId: $chatMessageId, content: $content) {
                    chatMessage {
                        id
                        message {
                            content
                        }
                    }
                }
            }
        '''
        response = self.query(
            query=query,
            variables={'chatMessageId': self.chat_message4.id, 'content': 'Hello World'},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        
        content = response.json()
        
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['updateChatMessage']['chatMessage']['message']['content'], 'Hello World')

        