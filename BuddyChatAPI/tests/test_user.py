from ..models import CustomUser
from graphene_django.utils.testing import GraphQLTestCase

# Create your tests here.

class UserTestCase(GraphQLTestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='test', first_name='test', last_name='test', password="123456789Test", email="test@buddy-chat.com", phone="+201234567890")
        self.user2 = CustomUser.objects.create_user(username='test1', first_name='test1', last_name='test1', password="113456789Test", email="test1@buddy-chat.com", phone="+201234567891")
        self.user1.save()
        self.user2.save()
        # Repeated mutation for testing
        self.create_user_mutation = '''
            mutation CreateUser($username: String!, $email: String!, $password: String!, $phone: String!, $firstName: String!, $lastName: String!) {
                createUser(username: $username, email: $email, password: $password, phone: $phone, firstName: $firstName, lastName: $lastName) {
                    user {
                        id
                        username
                        firstName
                        lastName
                    }
                }
            }
        '''
        
    def test_query_users(self):
        response = self.query(
            '''
            query {
                users {
                    edges {
                        node {
                            id
                            username
                            firstName
                            lastName
                        }
                    }
                }
            }
            '''
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['users']['edges']), 2)
        self.assertEqual(content['data']['users']['edges'][1]['node']['username'], 'test')
    
    def test_query_user(self):
        query = '''
            query user($id: Int!) {
                user(id: $id) {
                    id
                    username
                    firstName
                    lastName
                }
            }
        '''
        response = self.query(query=query, variables={'id': self.user1.id})
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['user']['username'], 'test')
        
    def test_create_user_invalid_email(self):
        response = self.query(query=self.create_user_mutation, variables={'username': 'test2', 'email': 'a@g', 'password': '123456789Test', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'})
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid email: a@g')
    
    def test_create_user_invalid_phone(self):
        response = self.query(query=self.create_user_mutation, variables={'username': 'test2', 'email': 'a@g.com', 'password': '123456789Test', 'phone': '+20123456789', 'firstName': 'test2', 'lastName': 'test2'})
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Phone number must be 13 characters long')
        
    def test_create_user_invalid_password(self):
        # check for digits in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@g.com', 'password': 'aaaaaaaa', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one digit')
        
        # check for letters in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one letter')
        
        # check for uppercase in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789test', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one uppercase letter')
        
        # check for lowercase in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789TEST', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one lowercase letter')
        
        
    def test_create_user_invalid_username(self):
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 't', 'email': 'a@f.com', 'password': '123456789Test', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Username must be at least 4 characters long')
        
    def test_create_user_invalid_first_name(self):
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phone': '+201234567897', 'firstName': 't', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'First name must be at least 2 characters long')
        
    def test_create_user_invalid_last_name(self):
        response = self.query(
                query=self.create_user_mutation, 
                variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 't'}
            )
                
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Last name must be at least 2 characters long')
        
    def test_create_user(self):
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phone': '+201234567897', 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createUser']['user']['username'], 'test2')
        self.assertEqual(content['data']['createUser']['user']['firstName'], 'test2')
        self.assertEqual(content['data']['createUser']['user']['lastName'], 'test2')
        