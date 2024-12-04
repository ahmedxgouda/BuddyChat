from ..models import CustomUser
from graphene_django.utils.testing import GraphQLTestCase

# Create your tests here.

class UserTestCase(GraphQLTestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='test', first_name='test', last_name='test', password="123456789Test", email="test@buddy-chat.com", phone="+201234567890")
        self.user2 = CustomUser.objects.create_user(username='test1', first_name='test1', last_name='test1', password="113456789Test", email="test1@buddy-chat.com", phone="+201234567891")
        self.user1.save()
        self.user2.save()
        # Get token for updating and deleting
        query = '''
            mutation TokenAuth($username: String!, $password: String!) {
                
                tokenAuth(username: $username, password: $password) {
                    token
                }
            }
            '''
        response_token = self.query(query=query, variables={'username': 'test', 'password': '123456789Test'})
        self.user1_token = response_token.json()['data']['tokenAuth']['token']
        response_token = self.query(query=query, variables={'username': 'test1', 'password': '113456789Test'})
        self.user2_token = response_token.json()['data']['tokenAuth']['token']
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
        
    def test_update_user(self):
        query = '''
            mutation UpdateUser($firstName: String, $lastName: String, $profilePicture: String, $bio: String) {
                updateUser(firstName: $firstName, lastName: $lastName, profilePicture: $profilePicture, bio: $bio) {
                    user {
                        id
                        firstName
                        lastName
                        profilePic
                        bio
                    }
                }
            }
        '''
        response = self.query(
            query=query, 
            variables={'firstName': 'test3', 'lastName': 'test3', 'profilePicture': 'test3.jpg', 'bio': 'test3'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['updateUser']['user']['firstName'], 'test3')
        self.assertEqual(content['data']['updateUser']['user']['lastName'], 'test3')
        self.assertEqual(content['data']['updateUser']['user']['profilePic'], 'test3.jpg')
        self.assertEqual(content['data']['updateUser']['user']['bio'], 'test3')
        
    def test_change_password(self):
        query = '''
            mutation ChangePassword($oldPassword: String!, $newPassword: String!) {
                changePassword(oldPassword: $oldPassword, newPassword: $newPassword) {
                    user {
                        id
                    }
                }
            }
        '''
        response = self.query(
            query=query, 
            variables={'oldPassword': '123456789Test', 'newPassword': '123456789Test1'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['changePassword']['user']['id'], str(self.user1.id))
        
    def test_delete_user(self):
        query = '''
            mutation DeleteUser($password: String!) {
                deleteUser(password: $password) {
                    userId
                }
            }
        '''
        # Test invalid password
        response = self.query(
            query=query,
            variables={'password': '123456789Test'},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Please, enter valid credentials')
        
        user_id = self.user2.id
        # Test valid password
        response = self.query(
            query=query,
            variables={'password': '113456789Test'},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteUser']['userId'], user_id)
        self.assertEqual(CustomUser.objects.filter(id=user_id).count(), 0)
