from graphene_django.utils.testing import GraphQLTestCase
from ..models import UserGroup, CustomUser, GroupMember, GroupMessage, Message, UserGroupMemberCopy
from ..GraphQL.helpers import create_message
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
        self.group_message2 = GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message2)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message2)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message2)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message2)
        
        # Create group messages for message 3
        self.group_message3 = GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message3)
        
        GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message3)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message3)
        GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message3)
        
        # Create group messages for message 4
        self.group_message4 = GroupMessage.objects.create(user_group_copy=self.group_member_copy4, message=self.message4)
        
        self.group_member_copy1.last_message =  GroupMessage.objects.create(user_group_copy=self.group_member_copy1, message=self.message4)
        self.group_member_copy2.last_message = GroupMessage.objects.create(user_group_copy=self.group_member_copy2, message=self.message4)
        self.group_member_copy3.last_message = GroupMessage.objects.create(user_group_copy=self.group_member_copy3, message=self.message4)
        self.group_member_copy4.last_message = self.group_message4
        
        self.group_member_copy1.save()
        self.group_member_copy2.save()
        self.group_member_copy3.save()
        self.group_member_copy4.save()
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
                    message {
                        id
                        content
                        sender {
                            id
                        }
                    
                    }
                }
            }
        '''
        
        self.notifications_query = '''
            query User($id: ID!) {
                user(id: $id) {
                    notifications {
                        edges {
                            node {
                                id
                                message {
                                    id
                                    content
                                }
                            }
                        }
                    }
                }
            }
        '''
        
        # For the group to be deleted
        self.group_to_be_deleted = UserGroup.objects.create(title='test2', created_by=self.admin_user)
        self.group_to_be_deleted.save()
        member_to_be_deleted = GroupMember.objects.create(user_group=self.group_to_be_deleted, member=self.admin_user, is_admin=True)
        member_to_be_deleted.save()
        self.copy_to_be_deleted = UserGroupMemberCopy.objects.create(member=member_to_be_deleted)
        self.copy_to_be_deleted.save()
        
        self.group_to_be_deleted.members_count = 1
        self.group_to_be_deleted.save()
        
        self.member_copies_count = 5
        self.group_members_count = 5
        self.group_messages_count = 16
        
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
        self.assertEqual(len(content['data']['groups']['edges']), 2)
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
        groupCopyId = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy1.id)
        response = self.query(
            query=self.create_group_message_mutation,
            variables={'groupCopyId': groupCopyId, 'content': 'Hello from user1'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        self.group_messages_count += 4
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createGroupMessage']['message']['content'], 'Hello from user1')
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        
        # Check if the notification was created
        user2_global_id = Node.to_global_id('CustomUserType', self.user2.id)
        user3_global_id = Node.to_global_id('CustomUserType', self.user3.id)
        user4_global_id = Node.to_global_id('CustomUserType', self.user4.id)
        
        user2NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': user2_global_id},
            headers={'Authorization': f'JWT {self.user2_token}'}
        )
        user3NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': user3_global_id},
            headers={'Authorization': f'JWT {self.user3_token}'}
        )
        user4NotificationResponse = self.query(
            query=self.notifications_query,
            variables={'id': user4_global_id},
            headers={'Authorization': f'JWT {self.user4_token}'}
        )
        self.assertResponseNoErrors(user2NotificationResponse)
        self.assertResponseNoErrors(user3NotificationResponse)
        self.assertResponseNoErrors(user4NotificationResponse)
        user2NotificationsContent = user2NotificationResponse.json()
        user3NotificationsContent = user3NotificationResponse.json()
        user4NotificationsContent = user4NotificationResponse.json()
        self.assertEqual(len(user2NotificationsContent['data']['user']['notifications']["edges"]), 1)
        self.assertEqual(len(user3NotificationsContent['data']['user']['notifications']["edges"]), 1)
        # User4 is not a member of the group
        self.assertEqual(len(user4NotificationsContent['data']['user']['notifications']["edges"]), 0)
        
    def test_create_group_member(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        member_id = Node.to_global_id('CustomUserType', self.user4.id)
        response = self.query(
            '''
            mutation CreateGroupMember($groupCopyId: ID!, $memberId: ID!) {
                createGroupMember(groupCopyId: $groupCopyId, memberId: $memberId) {
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
            variables={'groupCopyId': group_copy_id, 'memberId': member_id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )

        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createGroupMember']['groupMember']['member']['id'], member_id)
        self.member_copies_count += 1
        self.group_members_count += 1
        self.assertEqual(len(UserGroupMemberCopy.objects.all()), self.member_copies_count)
        self.assertEqual(len(GroupMember.objects.all()), self.group_members_count)
        
    def test_assign_admin(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        member_id = Node.to_global_id('GroupMemberType', self.group_member3.id)
        response = self.query(
            '''
            mutation ChangeAdmin($groupCopyId: ID!, $memberId: ID!, $isAdmin: Boolean!) {
                changeAdmin(groupCopyId: $groupCopyId, memberId: $memberId, isAdmin: $isAdmin) {
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
            variables={'groupCopyId': group_copy_id, 'memberId': member_id, 'isAdmin': True},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )

        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['changeAdmin']['groupMember']['isAdmin'], True)

    def test_remove_member(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        member_id = Node.to_global_id('GroupMemberType', self.group_member3.id)
        response = self.query(
            '''
            mutation RemoveGroupMember($groupCopyId: ID!, $memberId: ID!) {
                removeGroupMember(groupCopyId: $groupCopyId, memberId: $memberId) {
                    success
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id, 'memberId': member_id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )

        self.member_copies_count -= 1
        self.group_members_count -= 1
        self.group_messages_count -= 4

        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(len(UserGroupMemberCopy.objects.all()), self.member_copies_count)
        self.assertEqual(content['data']['removeGroupMember']['success'], True)
        self.assertEqual(len(GroupMember.objects.all()), self.group_members_count)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        
    def test_delete_group(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        response = self.query(
            '''
            mutation DeleteGroup($groupCopyId: ID!) {
                deleteGroup(groupCopyId: $groupCopyId) {
                    success
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        self.group_messages_count -= 4
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteGroup']['success'], True)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        self.assertEqual(len(UserGroupMemberCopy.objects.all()), self.member_copies_count)
        self.assertEqual(len(GroupMember.objects.all()), self.group_members_count)
        
    def test_leave_group(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy1.id)
        response = self.query(
            '''
            mutation LeaveGroup($groupCopyId: ID!) {
                leaveGroup(groupCopyId: $groupCopyId) {
                    success
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        self.group_members_count -= 1
        self.member_copies_count -= 1
        self.group_messages_count -= 4
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['leaveGroup']['success'], True)
        self.assertEqual(len(GroupMember.objects.all()), self.group_members_count)
        self.assertEqual(len(UserGroupMemberCopy.objects.all()), self.member_copies_count)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        
    def test_remove_group_permanently(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.copy_to_be_deleted.id)
        response = self.query(
            '''
            mutation RemoveGroupPermanently($groupCopyId: ID!) {
                removeGroupPermanently(groupCopyId: $groupCopyId) {
                    success
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        self.member_copies_count -= 1
        self.group_members_count -= 1
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['removeGroupPermanently']['success'], True)
        self.assertEqual(len(GroupMember.objects.all()), self.group_members_count)
        self.assertEqual(len(UserGroupMemberCopy.objects.all()), self.member_copies_count)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        
    def test_delete_group_message(self):
        group_message_id = Node.to_global_id('GroupMessageType', self.group_message4.id)
        response = self.query(
            '''
            mutation DeleteGroupMessage($groupMessageId: ID!) {
                deleteGroupMessage(groupMessageId: $groupMessageId) {
                    success
                }
            }
            ''',
            variables={'groupMessageId': group_message_id},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        self.group_messages_count -= 1
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteGroupMessage']['success'], True)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)
        
    def test_unsend_group_message(self):
        group_message_id = Node.to_global_id('GroupMessageType', self.group_message1.id)
        response = self.query(
            '''
            mutation UnsendGroupMessage($groupMessageId: ID!) {
                unsendGroupMessage(groupMessageId: $groupMessageId) {
                    success
                }
            }
            ''',
            variables={'groupMessageId': group_message_id},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        self.group_messages_count -= 4
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['unsendGroupMessage']['success'], True)
        self.assertEqual(len(GroupMessage.objects.all()), self.group_messages_count)

    def test_update_group(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        response = self.query(
            '''
            mutation UpdateGroup($groupCopyId: ID!, $description: String) {
                updateGroup(groupCopyId: $groupCopyId, description: $description) {
                    groupCopy {
                        id
                        member {
                            userGroup {
                                id
                                description
                            }
                        }
                    }
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id, 'description': 'A description for this group'},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['updateGroup']['groupCopy']['member']['userGroup']['description'], 'A description for this group')
        
    def test_update_group_message(self):
        group_message_id = Node.to_global_id('GroupMessageType', self.group_message2.id)
        response = self.query(
            '''
            mutation UpdateGroupMessage($groupMessageId: ID!, $content: String) {
                updateGroupMessage(groupMessageId: $groupMessageId, content: $content) {
                    groupMessage {
                        id
                        message {
                            id
                            content
                        }
                    }
                }
            }
            ''',
            variables={'groupMessageId': group_message_id, 'content': 'Updated message'},
            headers={'Authorization': f'JWT {self.user1_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['updateGroupMessage']['groupMessage']['message']['content'], 'Updated message')
        
    def test_set_archive_group(self):
        group_copy_id = Node.to_global_id('UserGroupMemberCopyType', self.group_member_copy4.id)
        response = self.query(
            '''
            mutation SetArchiveGroup($groupCopyId: ID!, $isArchived: Boolean!) {
                setArchiveGroup(groupCopyId: $groupCopyId, isArchived: $isArchived) {
                    groupCopy {
                        id
                        isArchived
                    }
                }
            }
            ''',
            variables={'groupCopyId': group_copy_id, 'isArchived': True},
            headers={'Authorization': f'JWT {self.admin_token}'}
        )
        
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['setArchiveGroup']['groupCopy']['isArchived'], True)
