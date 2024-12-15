from ..models import CustomUser
from graphene_django.utils.testing import GraphQLTestCase
from graphene.relay import Node
# Create your tests here.

class UserTestCase(GraphQLTestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username='test', first_name='test', last_name='test', password="123456789Test", email="test@buddy-chat.com", phone="+201234567890")
        self.user2 = CustomUser.objects.create_user(username='test1', first_name='test1', last_name='test1', password="113456789Test", email="test1@buddy-chat.com", phone="+201234567891")
        self.user1.save()
        self.user2.save()
        self.user1.phone_numbers.create(number='1234587890', country_code='20')
        # Get token for updating and deleting
        query = '''
            mutation Login($username: String!, $password: String!) {
                
                login(username: $username, password: $password) {
                    token
                }
            }
            '''
        response_token = self.query(query=query, variables={'username': 'test', 'password': '123456789Test'})
        self.user1_token = response_token.json()['data']['login']['token']
        response_token = self.query(query=query, variables={'username': 'test1', 'password': '113456789Test'})
        self.user2_token = response_token.json()['data']['login']['token']
        # Repeated mutation for testing
        self.create_user_mutation = '''
            mutation CreateUser($username: String!, $email: String!, $password: String!, $firstName: String!, $lastName: String!, $phoneNumber: PhoneNumberInputType!) {
                createUser(username: $username, email: $email, password: $password, firstName: $firstName, lastName: $lastName, phoneNumber: $phoneNumber) {
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
            query user($id: ID!) {
                user(id: $id) {
                    id
                    username
                    firstName
                    lastName
                }
            }
        '''
        response = self.query(query=query, variables={'id': Node.to_global_id('CustomUserType', self.user1.id)})
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['user']['username'], 'test')
        
    def test_create_user_invalid_email(self):
        response = self.query(query=self.create_user_mutation, variables={'username': 'test2', 'email': 'a@g', 'password': '123456789Test', 'firstName': 'test2', 'lastName': 'test2', 'phoneNumber': {'number': '1234567890', 'countryCode': '20'}})
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Invalid email: a@g')
    
    def test_create_user_invalid_phone(self):
        response = self.query(query=self.create_user_mutation, variables={'username': 'test2', 'email': 'a@g.com', 'password': '123456789Test', 'firstName': 'test2', 'lastName': 'test2', 'phoneNumber': {'number': '12345', 'countryCode': '20'}})
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Phone number must be between 8 and 15 characters long')
        
    def test_create_user_invalid_password(self):
        # check for digits in password
        phone_number = {'number': '1234567890', 'countryCode': '20'}
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@g.com', 'password': 'aaaaaaaa', 'firstName': 'test2', 'lastName': 'test2', 'phoneNumber': phone_number}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one digit')
        
        # check for letters in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789',  'phoneNumber': phone_number, 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one letter')
        
        # check for uppercase in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789test','phoneNumber': phone_number, 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one uppercase letter')
        
        # check for lowercase in password
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789TEST', 'phoneNumber': phone_number, 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Password must contain at least one lowercase letter')
        
        
    def test_create_user_invalid_username(self):
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 't', 'email': 'a@f.com', 'password': '123456789Test', 'phoneNumber': {'number': '1234567895', 'countryCode': '20'}, 'firstName': 'test2', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Username must be at least 4 characters long')
        
    def test_create_user_invalid_first_name(self):
        phone_number = {'number': '1234567895', 'countryCode': '20'}
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phoneNumber': phone_number, 'firstName': 't', 'lastName': 'test2'}
        )
        
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'First name must be at least 2 characters long')
        
    def test_create_user_invalid_last_name(self):
        phone_number = {'number': '1234567895', 'countryCode': '20'}
        response = self.query(
                query=self.create_user_mutation, 
                variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phoneNumber': phone_number, 'firstName': 'test2', 'lastName': 't'}
            )
                
        content = response.json()
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], 'Last name must be at least 2 characters long')
        
    def test_create_user(self):
        phone_number = {'number': '1234567895', 'countryCode': '20'}
        response = self.query(
            query=self.create_user_mutation, 
            variables={'username': 'test2', 'email': 'a@f.com', 'password': '123456789Test', 'phoneNumber': phone_number, 'firstName': 'test2', 'lastName': 'test2'}
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
        self.assertEqual(content['data']['changePassword']['user']['id'], Node.to_global_id('CustomUserType', self.user1.id))
        
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

    def test_add_phone_number(self):
        query = '''
            mutation AddPhoneNumber($number: String!, $countryCode: String!) {
                addPhoneNumber(number: $number, countryCode: $countryCode) {
                    phoneNumber {
                        number
                        countryCode
                    }
                }
            }
        '''
        response = self.query(
            query=query,
            variables={'number': '1234567836', 'countryCode': '20'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['addPhoneNumber']['phoneNumber']['number'], '1234567836')
        self.assertEqual(content['data']['addPhoneNumber']['phoneNumber']['countryCode'], '20')
        
    def test_remove_phone_number(self):
        query = '''
            mutation RemovePhoneNumber($phone_id: Int!) {
                removePhoneNumber(phoneId: $phone_id) {
                    phoneId
                }
            }
        '''
        phone = self.user1.phone_numbers.first()
        phone_id = phone.id
        response = self.query(
            query=query,
            variables={'phone_id': phone_id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['removePhoneNumber']['phoneId'], phone_id)
        self.assertEqual(self.user1.phone_numbers.count(), 0)
