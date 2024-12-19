# 📊 BuddyChat API Documentation

## Table of Contents

- [Overview](#overview)
- [Queries](#queries)
  - [users](#users)
  - [chats](#chats)
  - [groups](#groups)
  - [notifications](#notifications)
  - [chat](#chat)
  - [group](#group)
  - [user](#user)
- [Mutations](#mutations)
  - [createChat](#createchat)
  - [createChatMessage](#createchatmessage)
  - [deleteChat](#deletechat)
  - [updateChatMessage](#updatechatmessage)
  - [unsendChatMessage](#unsendchatmessage)
  - [deleteChatMessage](#deletechatmessage)
  - [setChatMessageAsRead](#setchatmessageasread)
  - [setChatArchived](#setchatarchived)
  - [createSelfChat](#createselfchat)
  - [createGroup](#creategroup)
  - [createGroupMessage](#creategroupmessage)
  - [createGroupMember](#creategroupmember)
  - [changeAdmin](#changeadmin)
  - [updateGroup](#updategroup)
  - [deleteGroup](#deletegroup)
  - [updateGroupMessage](#updategroupmessage)
  - [deleteGroupMessage](#deletegroupmessage)
  - [unsendGroupMessage](#unsendgroupmessage)
  - [removeGroupMember](#removegroupmember)
  - [leaveGroup](#leavegroup)
  - [removeGroupPermanently](#removegrouppermanently)
  - [setArchiveGroup](#setarchivegroup)
  - [login](#login)
  - [refreshToken](#refreshtoken)
  - [verifyToken](#verifytoken)
  - [revokeToken](#revoketoken)
  - [createUser](#createuser)
  - [addPhoneNumber](#addphonenumber)
  - [removePhoneNumber](#removephonenumber)
  - [updateUser](#updateuser)
  - [changePassword](#changepassword)
  - [deleteUser](#deleteuser)
  - [setNotificationRead](#setnotificationread)

## Overview

This document provides an overview of the BuddyChat API, including the GraphQL schema for queries and mutations.

## Queries

- **users**(offset: Int, before: String, after: String, first: Int, last: Int, username: String, firstName: String, lastName: String) → `CustomUserTypeConnection`
  *Description:* None

- **chats**(offset: Int, before: String, after: String, first: Int, last: Int, archived: Boolean) → `ChatTypeConnection`
  *Description:* None

- **groups**(offset: Int, before: String, after: String, first: Int, last: Int, isArchived: Boolean) → `UserGroupMemberCopyTypeConnection`
  *Description:* None

- **notifications**(offset: Int, before: String, after: String, first: Int, last: Int, isRead: Boolean) → `NotificationTypeConnection`
  *Description:* None

- **chat**(id: ID) → `ChatType`
  *Description:* None

- **group**(id: ID) → `UserGroupMemberCopyType`
  *Description:* None

- **user**(id: ID) → `CustomUserType`
  *Description:* None

### CustomUserTypeConnection

**Description:** None

```graphql
type CustomUserTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### PageInfo

**Description:** The Relay compliant `PageInfo` type, containing data necessary to paginate this connection.

```graphql
type PageInfo {
- **hasNextPage**() → `Boolean`
  *Description:* When paginating forwards, are there more items?

- **hasPreviousPage**() → `Boolean`
  *Description:* When paginating backwards, are there more items?

- **startCursor**() → `String`
  *Description:* When paginating backwards, the cursor to continue.

- **endCursor**() → `String`
  *Description:* When paginating forwards, the cursor to continue.

}

```

### CustomUserTypeEdge

**Description:** A Relay edge containing a `CustomUserType` and its cursor.

```graphql
type CustomUserTypeEdge {
- **node**() → `CustomUserType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### CustomUserType

**Description:** None

```graphql
type CustomUserType {
- **id**() → `ID`
  *Description:* The ID of the object

- **lastLogin**() → `DateTime`
  *Description:* None

- **username**() → `String`
  *Description:* Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.

- **firstName**() → `String`
  *Description:* None

- **lastName**() → `String`
  *Description:* None

- **email**() → `String`
  *Description:* None

- **isActive**() → `Boolean`
  *Description:* Designates whether this user should be treated as active. Unselect this instead of deleting accounts.

- **dateJoined**() → `DateTime`
  *Description:* None

- **phone**() → `String`
  *Description:* None

- **bio**() → `String`
  *Description:* None

- **profilePic**() → `String`
  *Description:* None

- **updatedAt**() → `DateTime`
  *Description:* None

- **phoneNumbers**() → `PhoneNumberType`
  *Description:* None

- **sentMessages**() → `None`
  *Description:* None

- **chats**(offset: Int, before: String, after: String, first: Int, last: Int, archived: Boolean) → `ChatTypeConnection`
  *Description:* None

- **createdGroups**(offset: Int, before: String, after: String, first: Int, last: Int) → `UserGroupTypeConnection`
  *Description:* None

- **userGroups**(offset: Int, before: String, after: String, first: Int, last: Int) → `GroupMemberTypeConnection`
  *Description:* None

- **notifications**(offset: Int, before: String, after: String, first: Int, last: Int, isRead: Boolean) → `NotificationTypeConnection`
  *Description:* None

}

```

### PhoneNumberType

**Description:** None

```graphql
type PhoneNumberType {
- **id**() → `ID`
  *Description:* None

- **number**() → `String`
  *Description:* None

- **countryCode**() → `String`
  *Description:* None

- **user**() → `CustomUserType`
  *Description:* None

}

```

### MessageType

**Description:** None

```graphql
type MessageType {
- **id**() → `ID`
  *Description:* None

- **sender**() → `CustomUserType`
  *Description:* None

- **content**() → `String`
  *Description:* None

- **date**() → `DateTime`
  *Description:* None

- **readAt**() → `DateTime`
  *Description:* None

- **chatMessages**(offset: Int, before: String, after: String, first: Int, last: Int) → `ChatMessageTypeConnection`
  *Description:* None

- **groupMessages**(offset: Int, before: String, after: String, first: Int, last: Int) → `GroupMessageTypeConnection`
  *Description:* None

- **notifications**(offset: Int, before: String, after: String, first: Int, last: Int) → `NotificationTypeConnection`
  *Description:* None

- **attachments**() → `None`
  *Description:* None

}

```

### ChatMessageTypeConnection

**Description:** None

```graphql
type ChatMessageTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### ChatMessageTypeEdge

**Description:** A Relay edge containing a `ChatMessageType` and its cursor.

```graphql
type ChatMessageTypeEdge {
- **node**() → `ChatMessageType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### ChatMessageType

**Description:** None

```graphql
type ChatMessageType {
- **id**() → `ID`
  *Description:* The ID of the object

- **message**() → `MessageType`
  *Description:* None

- **chat**() → `ChatType`
  *Description:* None

- **lastMessage**(offset: Int, before: String, after: String, first: Int, last: Int) → `ChatTypeConnection`
  *Description:* None

}

```

### ChatType

**Description:** None

```graphql
type ChatType {
- **id**() → `ID`
  *Description:* The ID of the object

- **user**() → `CustomUserType`
  *Description:* None

- **otherUser**() → `CustomUserType`
  *Description:* None

- **archived**() → `Boolean`
  *Description:* None

- **lastMessage**() → `ChatMessageType`
  *Description:* None

- **chatMessages**(offset: Int, before: String, after: String, first: Int, last: Int) → `ChatMessageTypeConnection`
  *Description:* None

}

```

### ChatTypeConnection

**Description:** None

```graphql
type ChatTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### ChatTypeEdge

**Description:** A Relay edge containing a `ChatType` and its cursor.

```graphql
type ChatTypeEdge {
- **node**() → `ChatType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### GroupMessageTypeConnection

**Description:** None

```graphql
type GroupMessageTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### GroupMessageTypeEdge

**Description:** A Relay edge containing a `GroupMessageType` and its cursor.

```graphql
type GroupMessageTypeEdge {
- **node**() → `GroupMessageType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### GroupMessageType

**Description:** None

```graphql
type GroupMessageType {
- **id**() → `ID`
  *Description:* The ID of the object

- **message**() → `MessageType`
  *Description:* None

- **userGroupCopy**() → `UserGroupMemberCopyType`
  *Description:* None

- **lastMessage**(offset: Int, before: String, after: String, first: Int, last: Int) → `UserGroupMemberCopyTypeConnection`
  *Description:* None

}

```

### UserGroupMemberCopyType

**Description:** None

```graphql
type UserGroupMemberCopyType {
- **id**() → `ID`
  *Description:* The ID of the object

- **member**() → `GroupMemberType`
  *Description:* None

- **isArchived**() → `Boolean`
  *Description:* None

- **lastMessage**() → `GroupMessageType`
  *Description:* None

- **groupMessages**(offset: Int, before: String, after: String, first: Int, last: Int) → `GroupMessageTypeConnection`
  *Description:* None

}

```

### GroupMemberType

**Description:** None

```graphql
type GroupMemberType {
- **id**() → `ID`
  *Description:* The ID of the object

- **userGroup**() → `UserGroupType`
  *Description:* None

- **member**() → `CustomUserType`
  *Description:* None

- **joinedAt**() → `DateTime`
  *Description:* None

- **isAdmin**() → `Boolean`
  *Description:* None

- **groupMember**(offset: Int, before: String, after: String, first: Int, last: Int) → `UserGroupMemberCopyTypeConnection`
  *Description:* None

}

```

### UserGroupType

**Description:** None

```graphql
type UserGroupType {
- **id**() → `ID`
  *Description:* The ID of the object

- **title**() → `String`
  *Description:* None

- **description**() → `String`
  *Description:* None

- **membersCount**() → `Int`
  *Description:* None

- **createdBy**() → `CustomUserType`
  *Description:* None

- **groupImage**() → `String`
  *Description:* None

- **updatedAt**() → `DateTime`
  *Description:* None

- **members**(offset: Int, before: String, after: String, first: Int, last: Int) → `GroupMemberTypeConnection`
  *Description:* None

}

```

### GroupMemberTypeConnection

**Description:** None

```graphql
type GroupMemberTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### GroupMemberTypeEdge

**Description:** A Relay edge containing a `GroupMemberType` and its cursor.

```graphql
type GroupMemberTypeEdge {
- **node**() → `GroupMemberType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### UserGroupMemberCopyTypeConnection

**Description:** None

```graphql
type UserGroupMemberCopyTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### UserGroupMemberCopyTypeEdge

**Description:** A Relay edge containing a `UserGroupMemberCopyType` and its cursor.

```graphql
type UserGroupMemberCopyTypeEdge {
- **node**() → `UserGroupMemberCopyType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### NotificationTypeConnection

**Description:** None

```graphql
type NotificationTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### NotificationTypeEdge

**Description:** A Relay edge containing a `NotificationType` and its cursor.

```graphql
type NotificationTypeEdge {
- **node**() → `NotificationType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

### NotificationType

**Description:** None

```graphql
type NotificationType {
- **id**() → `ID`
  *Description:* The ID of the object

- **message**() → `MessageType`
  *Description:* None

- **receiver**() → `CustomUserType`
  *Description:* None

- **isRead**() → `Boolean`
  *Description:* None

}

```

### AttachmentType

**Description:** None

```graphql
type AttachmentType {
- **id**() → `ID`
  *Description:* None

- **message**() → `MessageType`
  *Description:* None

- **file**() → `String`
  *Description:* None

}

```

### UserGroupTypeConnection

**Description:** None

```graphql
type UserGroupTypeConnection {
- **pageInfo**() → `PageInfo`
  *Description:* Pagination data for this connection.

- **edges**() → `None`
  *Description:* Contains the nodes in this connection.

}

```

### UserGroupTypeEdge

**Description:** A Relay edge containing a `UserGroupType` and its cursor.

```graphql
type UserGroupTypeEdge {
- **node**() → `UserGroupType`
  *Description:* The item at the end of the edge

- **cursor**() → `String`
  *Description:* A cursor for use in pagination

}

```

## Mutations

- **createChat**(otherUserId: ID) → `CreateChat`
  *Description:* None

- **createChatMessage**(chatId: ID, content: String) → `CreateChatMessage`
  *Description:* None

- **deleteChat**(chatId: ID) → `DeleteChat`
  *Description:* None

- **updateChatMessage**(chatMessageId: ID, content: String) → `UpdateChatMessage`
  *Description:* None

- **unsendChatMessage**(chatMessageId: ID) → `UnsendChatMessage`
  *Description:* None

- **deleteChatMessage**(chatMessageId: ID) → `DeleteChatMessage`
  *Description:* None

- **setChatMessageAsRead**(chatMessageId: ID) → `SetChatMessageAsRead`
  *Description:* None

- **setChatArchived**(archived: Boolean, chatId: ID) → `SetChatArchived`
  *Description:* None

- **createSelfChat**() → `CreateSelfChat`
  *Description:* None

- **createGroup**(title: String) → `CreateGroup`
  *Description:* None

- **createGroupMessage**(content: String, groupCopyId: ID) → `CreateGroupMessage`
  *Description:* None

- **createGroupMember**(groupCopyId: ID, memberId: ID) → `CreateGroupMember`
  *Description:* None

- **changeAdmin**(groupCopyId: ID, isAdmin: Boolean, memberId: ID) → `ChangeAdmin`
  *Description:* None

- **updateGroup**(description: String, groupCopyId: ID, groupImage: String, title: String) → `UpdateGroup`
  *Description:* None

- **deleteGroup**(groupCopyId: ID) → `DeleteGroup`
  *Description:* None

- **updateGroupMessage**(content: String, groupMessageId: ID) → `UpdateGroupMessage`
  *Description:* None

- **deleteGroupMessage**(groupMessageId: ID) → `DeleteGroupMessage`
  *Description:* None

- **unsendGroupMessage**(groupMessageId: ID) → `UnsendGroupMessage`
  *Description:* None

- **removeGroupMember**(groupCopyId: ID, memberId: ID) → `RemoveGroupMember`
  *Description:* None

- **leaveGroup**(groupCopyId: ID) → `LeaveGroup`
  *Description:* None

- **removeGroupPermanently**(groupCopyId: ID) → `RemoveGroup`
  *Description:* None

- **setArchiveGroup**(groupCopyId: ID, isArchived: Boolean) → `SetArchiveGroup`
  *Description:* None

- **login**(username: None, password: None) → `ObtainJSONWebToken`
  *Description:* Obtain JSON Web Token mutation

- **refreshToken**(refreshToken: String) → `Refresh`
  *Description:* None

- **verifyToken**(token: String) → `Verify`
  *Description:* None

- **revokeToken**(refreshToken: String) → `Revoke`
  *Description:* None

- **createUser**(email: None, firstName: None, lastName: None, password: None, phone: String, phoneNumber: None, username: None) → `CreateUserWithPhoneNumber`
  *Description:* None

- **addPhoneNumber**(countryCode: None, number: None) → `AddPhoneNumber`
  *Description:* None

- **removePhoneNumber**(phoneId: None) → `RemovePhoneNumber`
  *Description:* None

- **updateUser**(bio: String, firstName: String, lastName: String, profilePicture: String) → `UpdateUser`
  *Description:* None

- **changePassword**(newPassword: String, oldPassword: String) → `ChangePassword`
  *Description:* None

- **deleteUser**(password: String) → `DeleteUser`
  *Description:* None

- **setNotificationRead**(notificationId: ID) → `SetNotificationAsRead`
  *Description:* None

### CreateChat

**Description:** None

```graphql
type CreateChat {
- **chat**() → `ChatType`
  *Description:* None

- **otherChat**() → `ChatType`
  *Description:* None

}

```

### CreateChatMessage

**Description:** None

```graphql
type CreateChatMessage {
- **chatMessage**() → `ChatMessageType`
  *Description:* None

}

```

### DeleteChat

**Description:** None

```graphql
type DeleteChat {
- **success**() → `Boolean`
  *Description:* None

}

```

### UpdateChatMessage

**Description:** None

```graphql
type UpdateChatMessage {
- **chatMessage**() → `ChatMessageType`
  *Description:* None

}

```

### UnsendChatMessage

**Description:** None

```graphql
type UnsendChatMessage {
- **success**() → `Boolean`
  *Description:* None

}

```

### DeleteChatMessage

**Description:** None

```graphql
type DeleteChatMessage {
- **success**() → `Boolean`
  *Description:* None

}

```

### SetChatMessageAsRead

**Description:** None

```graphql
type SetChatMessageAsRead {
- **chatMessage**() → `ChatMessageType`
  *Description:* None

}

```

### SetChatArchived

**Description:** None

```graphql
type SetChatArchived {
- **chat**() → `ChatType`
  *Description:* None

}

```

### CreateSelfChat

**Description:** None

```graphql
type CreateSelfChat {
- **chat**() → `ChatType`
  *Description:* None

}

```

### CreateGroup

**Description:** None

```graphql
type CreateGroup {
- **userGroup**() → `UserGroupType`
  *Description:* None

}

```

### CreateGroupMessage

**Description:** None

```graphql
type CreateGroupMessage {
- **message**() → `MessageType`
  *Description:* None

}

```

### CreateGroupMember

**Description:** None

```graphql
type CreateGroupMember {
- **groupMember**() → `GroupMemberType`
  *Description:* None

}

```

### ChangeAdmin

**Description:** None

```graphql
type ChangeAdmin {
- **groupMember**() → `GroupMemberType`
  *Description:* None

}

```

### UpdateGroup

**Description:** None

```graphql
type UpdateGroup {
- **groupCopy**() → `UserGroupMemberCopyType`
  *Description:* None

}

```

### DeleteGroup

**Description:** None

```graphql
type DeleteGroup {
- **success**() → `Boolean`
  *Description:* None

}

```

### UpdateGroupMessage

**Description:** None

```graphql
type UpdateGroupMessage {
- **groupMessage**() → `GroupMessageType`
  *Description:* None

}

```

### DeleteGroupMessage

**Description:** None

```graphql
type DeleteGroupMessage {
- **success**() → `Boolean`
  *Description:* None

}

```

### UnsendGroupMessage

**Description:** None

```graphql
type UnsendGroupMessage {
- **success**() → `Boolean`
  *Description:* None

}

```

### RemoveGroupMember

**Description:** None

```graphql
type RemoveGroupMember {
- **success**() → `Boolean`
  *Description:* None

}

```

### LeaveGroup

**Description:** None

```graphql
type LeaveGroup {
- **success**() → `Boolean`
  *Description:* None

}

```

### RemoveGroup

**Description:** None

```graphql
type RemoveGroup {
- **success**() → `Boolean`
  *Description:* None

}

```

### SetArchiveGroup

**Description:** None

```graphql
type SetArchiveGroup {
- **groupCopy**() → `UserGroupMemberCopyType`
  *Description:* None

}

```

### ObtainJSONWebToken

**Description:** Obtain JSON Web Token mutation

```graphql
type ObtainJSONWebToken {
- **payload**() → `GenericScalar`
  *Description:* None

- **refreshExpiresIn**() → `Int`
  *Description:* None

- **token**() → `String`
  *Description:* None

- **refreshToken**() → `String`
  *Description:* None

}

```

### Refresh

**Description:** None

```graphql
type Refresh {
- **payload**() → `GenericScalar`
  *Description:* None

- **refreshExpiresIn**() → `Int`
  *Description:* None

- **token**() → `String`
  *Description:* None

- **refreshToken**() → `String`
  *Description:* None

}

```

### Verify

**Description:** None

```graphql
type Verify {
- **payload**() → `GenericScalar`
  *Description:* None

}

```

### Revoke

**Description:** None

```graphql
type Revoke {
- **revoked**() → `Int`
  *Description:* None

}

```

### CreateUserWithPhoneNumber

**Description:** None

```graphql
type CreateUserWithPhoneNumber {
- **user**() → `CustomUserType`
  *Description:* None

- **phoneNumber**() → `PhoneNumberType`
  *Description:* None

}

```

### AddPhoneNumber

**Description:** None

```graphql
type AddPhoneNumber {
- **phoneNumber**() → `PhoneNumberType`
  *Description:* None

}

```

### RemovePhoneNumber

**Description:** None

```graphql
type RemovePhoneNumber {
- **phoneId**() → `Int`
  *Description:* None

}

```

### UpdateUser

**Description:** None

```graphql
type UpdateUser {
- **user**() → `CustomUserType`
  *Description:* None

}

```

### ChangePassword

**Description:** None

```graphql
type ChangePassword {
- **user**() → `CustomUserType`
  *Description:* None

}

```

### DeleteUser

**Description:** None

```graphql
type DeleteUser {
- **userId**() → `Int`
  *Description:* None

}

```

### SetNotificationAsRead

**Description:** None

```graphql
type SetNotificationAsRead {
- **notification**() → `NotificationType`
  *Description:* None

}

```

### Subscription

**Description:** None

```graphql
type Subscription {
- **chatMessage**() → `ChatMessageType`
  *Description:* None

}

```
