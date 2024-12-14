from graphene_django.utils.testing import GraphQLTestCase
from ..models import UserGroup, CustomUser, GroupMember, GroupMessage, Message, UserGroupMemberCopy
from ..GraphQL.helpers import create_group_member, create_message
from graphene.relay.node import Node

class GroupTestCase(GraphQLTestCase):
    def setUp(self):
        # Prepare the users
        self.admin_user = CustomUser.objects.create_user(username='testGroup', first_name='test', last_name='test', password="123456789Test", email="testGroup@gg.com", phone="+201234587890")
        self.user1 = CustomUser.objects.create_user(username='testGroup1', first_name='test1', last_name='test1', password="113456789Test", email="testGroup1@gg.com", phone="+201234867891")
        self.user2 = CustomUser.objects.create_user(username='testGroup2', first_name='test2', last_name='test2', password="113456789Test", email="testGroup2@gg.com", phone="+201234567882")
        self.user3 = CustomUser.objects.create_user(username='testGroup3', first_name='test3', last_name='test3', password="113456789Test", email="testGroup3@gg.com", phone="+201534567893")
        self.user4 = CustomUser.objects.create_user(username='testGroup4', first_name='test4', last_name='test4', password="113456789Test", email="testGroup4@gg.com", phone="+201034567894")
        self.admin_user.save()
        self.user1.save()
        self.user2.save()
        self.user3.save()
        self.user4.save()
        # Create group
        self.group = UserGroup.objects.create(title='test', created_by=self.admin_user)
        self.group.save()
        # Create group members
        self.group_member1 = GroupMember.objects.create(user_group=self.group, member=self.user1)
        self.group_member2 = GroupMember.objects.create(user_group=self.group, member=self.user2)
        self.group_member3 = GroupMember.objects.create(user_group=self.group, member=self.user3)
        self.admin_group_member = GroupMember.objects.create(user_group=self.group, member=self.admin_user, is_admin=True)
        
        self.group_member1.save()
        self.group_member2.save()
        self.group_member3.save()
        self.admin_group_member.save()
        self.group.members_count = 4
        self.group.save()
        
        self.group_member_copy1 = UserGroupMemberCopy.objects.create(member=self.group_member1)
        self.group_member_copy2 = UserGroupMemberCopy.objects.create(member=self.group_member2)
        self.group_member_copy3 = UserGroupMemberCopy.objects.create(member=self.group_member3)
        self.group_member_copy4 = UserGroupMemberCopy.objects.create(member=self.admin_group_member)
        
        self.group_member_copy1.save()
        self.group_member_copy2.save()
        self.group_member_copy3.save()
        self.group_member_copy4.save()
        # Create messages and group messages
        self.message1 = create_message(self.user1.id, 'Hello from user1')
        self.message2 = create_message(self.user1.id, 'Hello from user1')
        self.message3 = create_message(self.user2.id, 'Hello from user2')
        self.message4 = create_message(self.user3.id, 'Hello from user3')
        
        
        # Create group messages for message 1
        self.group_message1 = GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message1)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message1)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message1)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message1)
        
        # Create group messages for message 2
        self.group_message2 = GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message2)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message2)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message2)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message2)
        
        # Create group messages for message 3
        self.group_message3 = GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message3)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message3)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message3)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message3)
        
        # Create group messages for message 4
        self.group_message4 = GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message4)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message4)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message4)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message4)
        
        # Token for authentication
        token_query = '''
            mutation Login($username: String!, $password: String!) {
                login(username: $username, password: $password) {
                    token
                }
            }
            '''
        
        admin_token_response = self.query(
            query=token_query,
            variables={'username': self.admin_user.username, 'password': '123456789Test'}
        )
        user1_token_response = self.query(
            query=token_query,
            variables={'username': self.user1.username, 'password': '113456789Test'}
        )
        user2_token_response = self.query(
            query=token_query,
            variables={'username': self.user2.username, 'password': '113456789Test'}
        )
        user3_token_response = self.query(
            query=token_query,
            variables={'username': self.user3.username, 'password': '113456789Test'}
        )
        user4_token_response = self.query(
            query=token_query,
            variables={'username': self.user4.username, 'password': '113456789Test'}
        )
        self.admin_token = admin_token_response.json()['data']['login']['token']
        self.user1_token = user1_token_response.json()['data']['login']['token']
        self.user2_token = user2_token_response.json()['data']['login']['token']
        self.user3_token = user3_token_response.json()['data']['login']['token']
        self.user4_token = user4_token_response.json()['data']['login']['token']

        # Repeated mutation for testing
        self.create_group_mutation = '''
            mutation CreateGroup($title: String!) {
                createGroup(title: $title) {
                    userGroup {
                        id
                        title
                        description
                        membersCount
                        createdBy {
                            id
                            username
                        }
                    }
                }
            }
        '''
        self.create_group_message_mutation = '''
            mutation CreateGroupMessage($groupCopyId: ID!, $content: String!) {
                createGroupMessage(groupCopyId: $groupCopyId, content: $content) {
                    groupMessage {
                        id
                        message {
                            id
                            content
                            sender {
                                id
                            }
                        }
                    }
                }
            }
        '''
        
        self.notifications_query = '''
            query User($id: ID!) {
                user(id: $id) {
                    notifications {
                        id
                        message {
                            id
                            content
                        }
                    }
                }
            }
        '''
        
    def test_query_groups(self):
        response = self.query(
            '''
            query {
                groups {
                    edges {
                        node {
                            id
                            member {
                                userGroup {
                                    id
                                    title
                                    description
                                    membersCount
                                    createdBy {
                                        id
                                        username
                                    }
                                }
                            }
                        }
                    }
                }
            }
            ''',
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['groups']['edges']), 1)
        self.assertEqual(content['data']['groups']['edges'][0]['node']['member']['userGroup']['title'], 'test')
        
    def test_query_group(self):
        query = '''
            query group($id: ID!) {
                group(id: $id) {
                    id
                    member {
                        userGroup {
                            id
                            title
                            description
                            membersCount
                            createdBy {
                                id
                                username
                            }
                        }
                    }
                }
            }
        '''
        group_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy1.id)
        response = self.query(query=query, variables={'id': group_id}, headers={'Authorization': f'JWT {self.user1_token}'})
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['group']['member']['userGroup']['title'], 'test')
        
    def test_create_group(self):
        response = self.query(
            query=self.create_group_mutation,
            variables={'title': 'test2'},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createGroup']['userGroup']['title'], 'test2')
        
    def test_create_group_message(self):
        response = self.query(
            query=self.create_group_message_mutation,
            variables={'userGroupId': self.group.id, 'content': 'Hello from user1'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createGroupMessage']['groupMessage']['message']['sender']['id'], str(self.user1.id))
        
        # Check if the notification was created
        user2NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': self.user2.id},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        user3NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': self.user3.id},
            headers={'Authorization': f'JWT {self.user3_token}'}
        )
        user4NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': self.user4.id},
            headers={'Authorization': f'JWT {self.user4_token}'}
        )
        self.assertResponseNoErrors(user2NotificationResponse)
        self.assertResponseNoErrors(user3NotificationResponse)
        self.assertResponseNoErrors(user4NotificationResponse)
        user2NotificationsContent = user2NotificationResponse.json()
        user3NotificationsContent = user3NotificationResponse.json()
        user4NotificationsContent = user4NotificationResponse.json()
        self.assertEqual(len(user2NotificationsContent['data']['user']['notifications']), 1)
        self.assertEqual(len(user3NotificationsContent['data']['user']['notifications']), 1)
        # User4 is not a member of the group
        self.assertEqual(len(user4NotificationsContent['data']['user']['notifications']), 0)
        
    def test_create_group_member(self):
        response = self.query(
            '''
            mutation CreateGroupMember($userGroupId: Int!, $memberId: Int!) {
                createGroupMember(userGroupId: $userGroupId, memberId: $memberId) {
                    groupMember {
                        id
                        userGroup {
                            id
                        }
                        member {
                            id
                        }
                    }
                }
            }
            ''',
            variables={'userGroupId': self.group.id, 'memberId': self.user4.id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )

        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createGroupMember']['groupMember']['member']['id'], str(self.user4.id))
        
    def test_assign_admin(self):
        response = self.query(
            '''
            mutation AssignAdmin($userGroupId: Int!, $memberId: Int!) {
                assignAdmin(userGroupId: $userGroupId, memberId: $memberId) {
                    groupMember {
                        id
                        userGroup {
                            id
                        }
                        member {
                            id
                        }
                        isAdmin
                    }
                }
            }
            ''',
            variables={'userGroupId': self.group.id, 'memberId': self.user1.id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )

        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['assignAdmin']['groupMember']['isAdmin'], True)
