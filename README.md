# 📊 BuddyChat API Documentation

## Table of Contents

- [Overview](#overview)
- [UML Model Diagram](#uml-model-diagram)
- [Endpoint](#endpoint)
- [Queries](#queries)
- [Mutations](#mutations)
- [Subscriptions](#subscriptions)
  - [Approach](#approach)
  - [Message Structure](#message-structure)
  - [Message Operations Table](#message-operations-table)
  - [Example Message](#example-message)
- [Types](#types)
  - [CustomUser](#customuser)
  - [PhoneNumber](#phonenumber)
  - [PhoneNumberInput](#phonenumberinput)
  - [Message](#message)
  - [Chat](#chat)
  - [ChatMessage](#chatmessage)
  - [UserGroup](#usergroup)
  - [GroupMessage](#groupmessage)
  - [GroupMember](#groupmember)
  - [Attachment](#attachment)
  - [Notification](#notification)
  - [UserGroupMemberCopy](#usergroupmembercopy)
- [Mutation Types](#mutation-types)
  - [CreateGroup](#creategroup)
  - [CreateGroupMessage](#creategroupmessage)
  - [CreateGroupMember](#creategroupmember)
  - [ChangeAdmin](#changeadmin)
  - [UpdateGroup](#updategroup)
  - [DeleteGroup](#deletegroup)
  - [UpdateGroupMessage](#updategroupmessage)
  - [DeleteGroupMessage](#deletegroupmessage)
  - [UnsendGroupMessage](#unsendgroupmessage)
  - [RemoveGroupMember](#removegroupmember)
  - [LeaveGroup](#leavegroup)
  - [RemoveGroupPermanently](#removegrouppermanently)
  - [SetArchiveGroup](#setarchivegroup)
  - [SetNotificationAsRead](#setnotificationasread)
  - [CreateUser](#createuser)
  - [UpdateUser](#updateuser)
  - [ChangePassword](#changepassword)
  - [DeleteUser](#deleteuser)
  - [CreateUser](#createuser)
  - [AddPhoneNumber](#addphonenumber)
  - [RemovePhoneNumber](#removephonenumber)
  - [CreateChat](#createchat)
  - [CreateSelfChat](#createselfchat)
  - [CreateChatMessage](#createchatmessage)
  - [UpdateChatMessage](#updatechatmessage)
  - [DeleteChatMessage](#deletechatmessage)
  - [UnsendChatMessage](#unsendchatmessage)
  - [DeleteChat](#deletechat)
  - [SetChatArchived](#setchatarchived)
  - [SetChatMessageAsRead](#setchatmessageasread)
- [Subscription Types](#subscription-types)
  - [Subscribe](#subscribe)
- [Other Features](#other-features)
  - [Throttling](#throttling)
  - [Pagination](#pagination)
  - [Filtering](#filtering)
- [Conclusion](#conclusion)

## Overview

This is the API documentation for the BuddyChat API. The API is built with Django and GraphQL using graphene. The API introduces a chat system with the following features:

- User registration and authentication
- Chat system
- Group chat system
- Notifications
- Real-time chat messages
- Copy of messages for each user which leads to the ability to delete messages for each user

## UML Model Diagram

![Model Diagram](./model.drawio.png)

## Endpoint

The API endpoint is `/graphql`.

## Queries

- `users`: The users in the system
- `chats`: The chats for the current user
- `groups`: The group copies for the current user
- `notifications`: The notifications for the current user
- `chat`: Resolve a chat for the current user
- `group`: Resolve a group copy for the current user
- `user`: Resolve a user

## Mutations

- `setNotificationRead`: Set a notification as read
- `login`: Login to the API. Returns a token
- `refreshToken`: Refresh the token
- `verifyToken`: Verify the token
- `revokeToken`: Revoke the token
- `createUser`: Create a user with a phone number
- `addPhoneNumber`: Add a phone number to the current user
- `removePhoneNumber`: Remove a phone number from the current user
- `updateUser`: Update the current user's data
- `changePassword`: Change the current user's password
- `deleteUser`: Delete the current user
- `createGroup`: A mutation to create a group. The creator is automatically added as an admin, and a group member copy is created for the creator
- `createGroupMessage`: A mutation to create a group message. A group message is created for each group member, and a notification is created for each group member
- `createGroupMember`: A mutation to add a member to a group
- `changeAdmin`: A mutation to change the admin status of a group member
- `updateGroup`: A mutation to update a group
- `deleteGroup`: A mutation to delete a group. Messages are deleted for the group copy of the current user
- `updateGroupMessage`: A mutation to update a group message
- `deleteGroupMessage`: A mutation to delete a group message. Deletes the message for the group copy of the current user
- `unsendGroupMessage`: A mutation to unsend a group message. Deletes the message for all group members
- `removeGroupMember`: A mutation to remove a member from a group
- `leaveGroup`: A mutation to leave a group
- `removeGroupPermanently`: A mutation to remove a group permanently
- `setArchiveGroup`: A mutation to archive a group
- `createChat`: A mutation to create two chat copies for two users
- `createSelfChat`: A mutation to create a chat copy for the current user
- `createChatMessage`: A mutation to create a chat message. A chat message is created for each user, and a notification is created for the other user
- `updateChatMessage`: A mutation to update a chat message
- `deleteChatMessage`: A mutation to delete a chat message. Deletes the message for the chat copy of the current user
- `unsendChatMessage`: A mutation to unsend a chat message. Deletes the message for both chat copies
- `deleteChat`: A mutation to delete a chat. Messages are deleted for the chat copy of the current user
- `setArchiveChat`: A mutation to archive or unarchive a chat
- `setChatMessageAsRead`: A mutation to set a chat message as read

## Subscriptions

### Approach

- The API uses `Django Channels` with `signals` to send messages to the client. The messages which are sent are not much like `GraphQL` subscriptions. They are more like `WebSocket` messages. Because of `Graphene` limitations, I made a workaround to send messages like `WebSocket` messages. The subprotocol used is `graphql-transport-ws`.
- The subscription is done by sending a `subscription` query to the API with the following structure:

    ```graphql
    subscription {
        subscribe {
            success
        }
    }
    ```

- This query is done to subscribe to the messages. The `success` field returns `True` and it is not used. The subscription is done by sending a `next` message to the client with the message payload.

### Message Structure

- All messages are sent as `next` messages and contain the field `id` which represents the subscription id.
- The message contains `payload` which contains the actual message.
- The `payload` message is an object with the following properties:
  - `type`: The type of the message. It is always `broadcast`.
  - `operation`: The operation which is done.
  - `payload`: The actual payload of the message.

### Message Operations Table

| Operation                | Description                                      |
|--------------------------|--------------------------------------------------|
| CHAT_MESSAGE_CREATED     | A new chat message has been created              |
| CHAT_MESSAGE_UPDATED     | An existing chat message has been updated        |
| CHAT_MESSAGE_DELETED     | A chat message has been deleted                  |
| CHAT_MESSAGE_UNSENT      | A chat message has been unsent                   |
| CHAT_MESSAGE_READ        | A chat message has been read                     |
| CHAT_DELETED             | A chat has been deleted                          |
| GROUP_MESSAGE_CREATED    | A new group message has been created             |
| GROUP_MESSAGE_UPDATED    | An existing group message has been updated       |
| GROUP_MESSAGE_DELETED    | A group message has been deleted                 |
| GROUP_MESSAGE_UNSENT     | A group message has been unsent                  |
| GROUP_MESSAGE_READ       | A group message has been read                    |
| GROUP_DELETED            | A group has been deleted                         |
| GROUP_UPDATED            | A group has been updated                         |
| GROUP_PERMANENTLY_REMOVED| A group has been permanently removed             |
| NOTIFICATION_CREATED     | A new notification has been created              |
| MEMBER_ADDED             | A new member has been added to a group           |
| MEMBER_REMOVED           | A member has been removed from a group           |
| MEMBER_LEFT              | A member has left a group                        |

### Example Message

```json
{
    "type": "next",
    "id": "b7455cd0-2363-481a-913e-74be16be060e",
    "payload": {
        "type": "broadcast",
        "operation": "CHAT_MESSAGE_CREATED",
        "payload": {
            "chatMessage": {
                "id": "GQo6U2hhdHRlY2g6MjI=",
                "message": {
                    "id": "GQo6TWVzc2FnZVR5cGU6MjA=",
                    "content": "Hello",
                    "sender": {
                        "id": "GQo6VXNlcjp1c2VyMQ=="
                    }
                },
                "chat": {
                    "id": "GQo6Q2hhdDpjaGF0MQ=="
                }
            }
        }
    }
}
```

## Types

### CustomUser

```graphql
type CustomUser {
    id: ID!
    username: String!
    firstName: String!
    lastName: String!
    email: String!
    phoneNumbers: [PhoneNumber]
    chats: [Chat]
    notifications: [Notification]
}
```

Description: The user type. It contains the user's information.

### PhoneNumber

```graphql
type PhoneNumber {
    id: ID!
    number: String!
    countryCode: String!
}
```

### PhoneNumberInput

```graphql
input PhoneNumberInput {
    number: String!
    countryCode: String!
}
```

### Message

```graphql
type Message {
    id: ID!
    content: String!
    readAt: DateTime
}
```

Description: The root message type which is the dependent type for the chat message and group message types.

### Chat

```graphql
type Chat {
    id: ID!
    user: CustomUser!
    otherUser: CustomUser!
    archived: Boolean!
    chat_messages: [ChatMessage]
}
```

Description: The chat type. Each user has a chat copy for each other user they have chatted with.

### ChatMessage

```graphql
type ChatMessage {
    id: ID!
    message: Message!
    chat: Chat!
}
```

Description: The chat message type. It contains the chat message information.

### UserGroup

```graphql
type UserGroup {
    id: ID!
    title: String!  
    description: String!
    members: [GroupMember]
}
```

Description: The root user group type. It contains the main information. GroupMember depends on this type.

### GroupMessage

```graphql
type GroupMessage {
    id: ID!
    message: Message!
    group_copy: UserGroupMemberCopy!
}
```

Description: The group message type. It contains the group message information.

### GroupMember

```graphql
type GroupMember {
    id: ID!
    user: CustomUser!
    group: UserGroup!
    isAdmin: Boolean!
    joinedAt: DateTime!
}
```

Description: The group member type. It contains the group member information.

### Attachment

```graphql
type Attachment {
    id: ID!
    file: String!
    message: Message!
}
```

### Notification

```graphql
type Notification {
    id: ID!
    message: Message!
    readAt: DateTime
}
```

### UserGroupMemberCopy

```graphql
type UserGroupMemberCopy {
    id: ID!
    member: GroupMember!
    isArchived: Boolean!
    group_messages: [GroupMessage]
}
```

Description: The user group member copy type. The user copy of the group, so that each user can have a copy of the group messages.

## Mutation Types

### CreateGroup

```graphql
type CreateGroup {
    userGroup: UserGroup
}
```

Description: A mutation to create a group. The creator is automatically added as an admin, and a group member copy is created for the creator.

### CreateGroupMessage

```graphql
type CreateGroupMessage {
    message: GroupMessage
}
```

Description: A mutation to create a group message. A group message is created for each group member, and a notification is created for each group member.

### CreateGroupMember

```graphql
type CreateGroupMember {
    groupMember: GroupMember
}
```

Description: A mutation to add a member to a group.

### ChangeAdmin

```graphql
type ChangeAdmin {
    groupMember: GroupMember
}
```

Description: A mutation to change the admin status of a group member.

### UpdateGroup

```graphql
type UpdateGroup {
    groupCopy: UserGroupMemberCopy
}
```

Description: A mutation to update a group.

### DeleteGroup

```graphql
type DeleteGroup {
    success: Boolean
}
```

Description: A mutation to delete a group. Messages are deleted for the group copy of the current user.

### UpdateGroupMessage

```graphql
type UpdateGroupMessage {
    groupMessage: GroupMessage
}
```

Description: A mutation to update a group message.

### DeleteGroupMessage

```graphql
type DeleteGroupMessage {
    success: Boolean
}
```

Description: A mutation to delete a group message. Deletes the message for the group copy of the current user.

### UnsendGroupMessage

```graphql
type UnsendGroupMessage {
    success: Boolean
}
```

Description: A mutation to unsend a group message. Deletes the message for all group members.

### RemoveGroupMember

```graphql
type RemoveGroupMember {
    success: Boolean
}
```

Description: A mutation to remove a member from a group.

### LeaveGroup

```graphql
type LeaveGroup {
    success: Boolean
}
```

Description: A mutation to leave a group.

### RemoveGroupPermanently

```graphql
type RemoveGroupPermanently {
    success: Boolean
}
```

Description: A mutation to remove a group permanently.

### SetArchiveGroup

```graphql
type SetArchiveGroup {
    groupCopy: UserGroupMemberCopy
}
```

Description: A mutation to archive a group.

### SetNotificationAsRead

```graphql
type SetNotificationAsRead {
    notification: Notification
}
```

Description: A mutation to set a notification as read.

### UpdateUser

```graphql
type UpdateUser {
    user: CustomUser
}
```

Description: Mutation to update the current user's data.

### ChangePassword

```graphql
type ChangePassword {
    user: CustomUser
}
```

Description: Mutation to change the current user's password.

### DeleteUser

```graphql
type DeleteUser {
    userId: Int
}
```

Description: Mutation to delete the current user.

### CreateUser

```graphql
type CreateUser {
    user: CustomUser
    phoneNumber: PhoneNumber
}
```

Description: Mutation to create a user with a phone number.

### AddPhoneNumber

```graphql
type AddPhoneNumber {
    phoneNumber: PhoneNumber
}
```

Description: Mutation to add a phone number to the current user.

### RemovePhoneNumber

```graphql
type RemovePhoneNumber {
    success: Boolean
}
```

Description: Mutation to remove a phone number from the current user.

### CreateChat

```graphql
type CreateChat {
    chat: Chat
    otherChat: Chat
}
```

Description: Mutation to create two chat copies for two users.

### CreateSelfChat

```graphql
type CreateSelfChat {
    chat: Chat
}
```

Description: Mutation to create a chat for the user.

### CreateChatMessage

```graphql
type CreateChatMessage {
    chatMessage: ChatMessage
}
```

Description: Mutation to create a chat message. A chat message is created for each user, and a notification is created for the other user.

### UpdateChatMessage

```graphql
type UpdateChatMessage {
    chatMessage: ChatMessage
}
```

Description: Mutation to update a chat message.

### DeleteChatMessage

```graphql
type DeleteChatMessage {
    success: Boolean
}
```

Description: Mutation to delete a chat message. Deletes the message for the chat copy of the current user.

### UnsendChatMessage

```graphql
type UnsendChatMessage {
    success: Boolean
}
```

Description: Mutation to unsend a chat message. Deletes the message for both chat copies.

### DeleteChat

```graphql
type DeleteChat {
    success: Boolean
}
```

Description: Mutation to delete a chat. Messages are deleted for the chat copy of the current user.

### SetChatArchived

```graphql
type SetChatArchived {
    chat: Chat
}
```

Description: Mutation to archive or unarchive a chat.

### SetChatMessageAsRead

```graphql
type SetChatMessageAsRead {
    chatMessage: ChatMessage
}
```

Description: Mutation to set a chat message as read.

## Subscription Types

### Subscribe

```graphql
type Subscribe {
    success: Boolean
}
```

Description: The success message is returned when the client subscribes to the messages.

## Other Features

### Throttling

To ensure fair usage and prevent abuse, the BuddyChat API implements throttling. This limits the number of requests a user can make to the API within a certain time frame. If the limit is exceeded, the API will return a `403` error response.

### Pagination

The BuddyChat API supports pagination for queries that return lists of items. This helps to manage large datasets by breaking them into smaller, more manageable chunks. Pagination is implemented using the `first` and `after` arguments for forward pagination, and `last` and `before` arguments for backward pagination. The API returns a `PageInfo` object that includes information about the current page and whether there are more pages available.

### Filtering

To provide more flexibility in querying data, the BuddyChat API supports filtering on various fields. Filters can be applied to queries to narrow down the results based on specific criteria. The available filters are documented for each query type.

## Conclusion

The BuddyChat API provides a comprehensive set of features for building a robust chat application. With support for user authentication, real-time messaging, group chats, notifications, and more, it offers a solid foundation for any chat-based application. The API is designed to be flexible and scalable, with features like throttling, pagination, and filtering to handle various use cases and ensure optimal performance. Whether you're building a simple chat app or a complex messaging platform, the BuddyChat API has you covered.
