from graphene_django.utils.testing import GraphQLTestCase
from ..models import Chat, CustomUser, ChatMessage, Message, Notification

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
        self.chat1 = Chat.objects.create(user1=self.user1, user2=self.user2)
        self.chat2 = Chat.objects.create(user1=self.user1, user2=self.user3)
        self.chat3 = Chat.objects.create(user1=self.user2, user2=self.user4)
        self.chat1.save()
        self.chat2.save()
        self.chat3.save()
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
        self.chat_message2 = ChatMessage.objects.create(chat=self.chat2, message=self.message2)
        self.chat_message3 = ChatMessage.objects.create(chat=self.chat3, message=self.message3)
        self.chat_message4 = ChatMessage.objects.create(chat=self.chat3, message=self.message4)
        self.chat_message1.save()
        self.chat_message2.save()
        self.chat_message3.save()
        self.chat_message4.save()
        
        self.chat1.last_message = self.chat_message1
        self.chat2.last_message = self.chat_message2
        self.chat3.last_message = self.chat_message4
        self.chat1.save()
        self.chat2.save()
        self.chat3.save()
        # Token for authentication
        token_query = '''
            mutation TokenAuth($username: String!, $password: String!) {
                tokenAuth(username: $username, password: $password) {
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
        
        self.user1_token = user1_token_response.json()['data']['tokenAuth']['token']
        self.user2_token = user2_token_response.json()['data']['tokenAuth']['token']
        # Repeated mutation for testing
        self.create_chat_mutation = '''
            mutation CreateChat($user1Id: Int!, $user2Id: Int!) {
                createChat(user1Id: $user1Id, user2Id: $user2Id) {
                    chat {
                        id
                        user1 {
                            id
                            username
                        }
                        user2 {
                            id
                            username
                        }
                    }
                }
            }
        '''
        self.create_chat_message_mutation = '''
            mutation CreateChatMessage($chatId: Int!, $content: String!) {
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
        
        
    def test_query_chats(self):
        response = self.query(
            '''
            query {
                chats {
                    edges {
                        node {
                            id
                            user1 {
                                id
                                username
                            }
                            user2 {
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
        self.assertEqual(content['data']['chats']['edges'][0]['node']['user1']['username'], 'test')
        
    def test_query_chat(self):
        response = self.query(
            '''
            query chat($id: Int!) {
                chat(id: $id) {
                    id
                    user1 {
                        id
                        username
                    }
                    user2 {
                        id
                        username
                    }
                }
            }
            ''',
            variables={'id': self.chat1.id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['chat']['user1']['username'], 'test')
        
    def test_create_chat(self):
        response = self.query(
            self.create_chat_mutation,
            variables={'user1Id': self.user1.id, 'user2Id': self.user1.id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createChat']['chat']['user1']['username'], 'test')
        self.assertEqual(content['data']['createChat']['chat']['user2']['username'], 'test')
        
    def test_create_chat_message(self):
        response = self.query(
            self.create_chat_message_mutation,
            variables={'chatId': self.chat1.id, 'content': 'Hello'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createChatMessage']['chatMessage']['message']['content'], 'Hello')
        self.assertEqual(content['data']['createChatMessage']['chatMessage']['message']['sender']['username'], 'test')
        
        # Check if notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.receiver.id, self.user2.id)
        self.assertEqual(notification.message.id, int(content['data']['createChatMessage']['chatMessage']['message']['id']))
        
    def test_create_chat_message_invalid_chat(self):
        response = self.query(
            self.create_chat_message_mutation,
            variables={'chatId': self.chat3.id, 'content': 'Hello'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'A user is not a member of this chat')

    def test_delete_chat(self):
        chat1_id = self.chat1.id
        response = self.query(
            '''
            mutation DeleteChat($chatId: Int!) {
                deleteChat(chatId: $chatId) {
                    chatId
                }
            }
            ''',
            variables={'chatId': self.chat1.id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteChat']['chatId'], chat1_id)
        self.assertEqual(Chat.objects.count(), 2)
        
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

        