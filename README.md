# 📊 BuddyChat API Documentation

## Overview

This file documents the GraphQL schema for BuddyChat API. The schema is divided into two sections: Queries, and Mutations.

## Queries

- **users**(offset: Int, before: String, after: String, first: Int, last: Int, username: String, firstName: String, lastName: String) → `CustomUserTypeConnection`
- **chats**(offset: Int, before: String, after: String, first: Int, last: Int, archived: Boolean) → `ChatTypeConnection`
- **groups**(offset: Int, before: String, after: String, first: Int, last: Int, isArchived: Boolean) → `UserGroupMemberCopyTypeConnection`
- **notifications**(offset: Int, before: String, after: String, first: Int, last: Int, isRead: Boolean) → `NotificationTypeConnection`
- **chat**(id: ID) → `ChatType`
- **group**(id: ID) → `UserGroupMemberCopyType`
- **user**(id: ID) → `CustomUserType`

### CustomUserTypeConnection

```graphql
type CustomUserTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [CustomUserTypeEdge]!
}

"""
The Relay compliant `PageInfo` type, containing data necessary to paginate this connection.
"""
```

### PageInfo

```graphql
type PageInfo {

  """When paginating forwards, are there more items?"""
  hasNextPage: Boolean!

  """When paginating backwards, are there more items?"""
  hasPreviousPage: Boolean!

  """When paginating backwards, the cursor to continue."""
  startCursor: String

  """When paginating forwards, the cursor to continue."""
  endCursor: String
}

"""A Relay edge containing a `CustomUserType` and its cursor."""
```

### CustomUserTypeEdge

```graphql
type CustomUserTypeEdge {

  """The item at the end of the edge"""
  node: CustomUserType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### CustomUserType

```graphql
type CustomUserType implements Node {

  """The ID of the object"""
  id: ID!
  lastLogin: DateTime

  """Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."""
  username: String!
  firstName: String!
  lastName: String!
  email: String

  """
  Designates whether this user should be treated as active. Unselect this instead of deleting accounts.
  """
  isActive: Boolean!
  dateJoined: DateTime!
  phone: String
  bio: String!
  profilePic: String!
  updatedAt: DateTime!
  phoneNumbers: [PhoneNumberType]
  sentMessages: [MessageType!]!
  chats(offset: Int, before: String, after: String, first: Int, last: Int, archived: Boolean): ChatTypeConnection
  createdGroups(offset: Int, before: String, after: String, first: Int, last: Int): UserGroupTypeConnection!
  userGroups(offset: Int, before: String, after: String, first: Int, last: Int): GroupMemberTypeConnection!
  notifications(offset: Int, before: String, after: String, first: Int, last: Int, isRead: Boolean): NotificationTypeConnection
}

"""An object with an ID"""
interface Node {
  """The ID of the object"""
  id: ID!
}

"""
The `DateTime` scalar type represents a DateTime
value as specified by
[iso8601](https://en.wikipedia.org/wiki/ISO_8601).
"""
scalar DateTime

```

### PhoneNumberType

```graphql
type PhoneNumberType {

  id: ID!
  number: String!
  countryCode: String!
  user: CustomUserType!
}

```

### MessageType

```graphql
type MessageType {

  id: ID!
  sender: CustomUserType!
  content: String!
  date: DateTime!
  readAt: DateTime
  chatMessages(offset: Int, before: String, after: String, first: Int, last: Int): ChatMessageTypeConnection!
  groupMessages(offset: Int, before: String, after: String, first: Int, last: Int): GroupMessageTypeConnection!
  notifications(offset: Int, before: String, after: String, first: Int, last: Int): NotificationTypeConnection!
  attachments: [AttachmentType!]!
}

```

### ChatMessageTypeConnection

```graphql
type ChatMessageTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [ChatMessageTypeEdge]!
}

"""A Relay edge containing a `ChatMessageType` and its cursor."""
```

### ChatMessageTypeEdge

```graphql
type ChatMessageTypeEdge {

  """The item at the end of the edge"""
  node: ChatMessageType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### ChatMessageType

```graphql
type ChatMessageType implements Node {

  """The ID of the object"""
  id: ID!
  message: MessageType!
  chat: ChatType!
  lastMessage(offset: Int, before: String, after: String, first: Int, last: Int): ChatTypeConnection!
}

```

### ChatType

```graphql
type ChatType implements Node {

  """The ID of the object"""
  id: ID!
  user: CustomUserType!
  otherUser: CustomUserType
  archived: Boolean!
  lastMessage: ChatMessageType
  chatMessages(offset: Int, before: String, after: String, first: Int, last: Int): ChatMessageTypeConnection!
}

```

### ChatTypeConnection

```graphql
type ChatTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [ChatTypeEdge]!
}

"""A Relay edge containing a `ChatType` and its cursor."""
```

### ChatTypeEdge

```graphql
type ChatTypeEdge {

  """The item at the end of the edge"""
  node: ChatType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### GroupMessageTypeConnection

```graphql
type GroupMessageTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [GroupMessageTypeEdge]!
}

"""A Relay edge containing a `GroupMessageType` and its cursor."""
```

### GroupMessageTypeEdge

```graphql
type GroupMessageTypeEdge {

  """The item at the end of the edge"""
  node: GroupMessageType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### GroupMessageType

```graphql
type GroupMessageType implements Node {

  """The ID of the object"""
  id: ID!
  message: MessageType!
  userGroupCopy: UserGroupMemberCopyType!
  lastMessage(offset: Int, before: String, after: String, first: Int, last: Int): UserGroupMemberCopyTypeConnection!
}

```

### UserGroupMemberCopyType

```graphql
type UserGroupMemberCopyType implements Node {

  """The ID of the object"""
  id: ID!
  member: GroupMemberType!
  isArchived: Boolean!
  lastMessage: GroupMessageType
  groupMessages(offset: Int, before: String, after: String, first: Int, last: Int): GroupMessageTypeConnection!
}

```

### GroupMemberType

```graphql
type GroupMemberType implements Node {

  """The ID of the object"""
  id: ID!
  userGroup: UserGroupType!
  member: CustomUserType!
  joinedAt: DateTime!
  isAdmin: Boolean!
  groupMember(offset: Int, before: String, after: String, first: Int, last: Int): UserGroupMemberCopyTypeConnection!
}

```

### UserGroupType

```graphql
type UserGroupType implements Node {

  """The ID of the object"""
  id: ID!
  title: String!
  description: String!
  membersCount: Int!
  createdBy: CustomUserType
  groupImage: String!
  updatedAt: DateTime!
  members(offset: Int, before: String, after: String, first: Int, last: Int): GroupMemberTypeConnection!
}

```

### GroupMemberTypeConnection

```graphql
type GroupMemberTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [GroupMemberTypeEdge]!
}

"""A Relay edge containing a `GroupMemberType` and its cursor."""
```

### GroupMemberTypeEdge

```graphql
type GroupMemberTypeEdge {

  """The item at the end of the edge"""
  node: GroupMemberType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### UserGroupMemberCopyTypeConnection

```graphql
type UserGroupMemberCopyTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [UserGroupMemberCopyTypeEdge]!
}

"""A Relay edge containing a `UserGroupMemberCopyType` and its cursor."""
```

### UserGroupMemberCopyTypeEdge

```graphql
type UserGroupMemberCopyTypeEdge {

  """The item at the end of the edge"""
  node: UserGroupMemberCopyType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### NotificationTypeConnection

```graphql
type NotificationTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [NotificationTypeEdge]!
}

"""A Relay edge containing a `NotificationType` and its cursor."""
```

### NotificationTypeEdge

```graphql
type NotificationTypeEdge {

  """The item at the end of the edge"""
  node: NotificationType

  """A cursor for use in pagination"""
  cursor: String!
}

```

### NotificationType

```graphql
type NotificationType implements Node {

  """The ID of the object"""
  id: ID!
  message: MessageType!
  receiver: CustomUserType!
  isRead: Boolean!
}

```

### AttachmentType

```graphql
type AttachmentType {

  id: ID!
  message: MessageType!
  file: String!
}

```

### UserGroupTypeConnection

```graphql
type UserGroupTypeConnection {

  """Pagination data for this connection."""
  pageInfo: PageInfo!

  """Contains the nodes in this connection."""
  edges: [UserGroupTypeEdge]!
}

"""A Relay edge containing a `UserGroupType` and its cursor."""
```

### UserGroupTypeEdge

```graphql
type UserGroupTypeEdge {

  """The item at the end of the edge"""
  node: UserGroupType

  """A cursor for use in pagination"""
  cursor: String!
}

```

## Mutations

- **createChat**(otherUserId: ID) → `CreateChat`
- **createChatMessage**(chatId: ID, content: String) → `CreateChatMessage`
- **deleteChat**(chatId: ID) → `DeleteChat`
- **updateChatMessage**(chatMessageId: ID, content: String) → `UpdateChatMessage`
- **unsendChatMessage**(chatMessageId: ID) → `UnsendChatMessage`
- **deleteChatMessage**(chatMessageId: ID) → `DeleteChatMessage`
- **setChatMessageAsRead**(chatMessageId: ID) → `SetChatMessageAsRead`
- **setChatArchived**(archived: Boolean, chatId: ID) → `SetChatArchived`
  createSelfChat: CreateSelfChat
- **createGroup**(title: String) → `CreateGroup`
- **createGroupMessage**(content: String, groupCopyId: ID) → `CreateGroupMessage`
- **createGroupMember**(groupCopyId: ID, memberId: ID) → `CreateGroupMember`
- **changeAdmin**(groupCopyId: ID, isAdmin: Boolean, memberId: ID) → `ChangeAdmin`
- **updateGroup**(description: String, groupCopyId: ID, groupImage: String, title: String) → `UpdateGroup`
- **deleteGroup**(groupCopyId: ID) → `DeleteGroup`
- **updateGroupMessage**(content: String, groupMessageId: ID) → `UpdateGroupMessage`
- **deleteGroupMessage**(groupMessageId: ID) → `DeleteGroupMessage`
- **unsendGroupMessage**(groupMessageId: ID) → `UnsendGroupMessage`
- **removeGroupMember**(groupCopyId: ID, memberId: ID) → `RemoveGroupMember`
- **leaveGroup**(groupCopyId: ID) → `LeaveGroup`
- **removeGroupPermanently**(groupCopyId: ID) → `RemoveGroup`
- **setArchiveGroup**(groupCopyId: ID, isArchived: Boolean) → `SetArchiveGroup`

  """Obtain JSON Web Token mutation"""
- **login**(username: String!, password: String!) → `ObtainJSONWebToken`
- **refreshToken**(refreshToken: String) → `Refresh`
- **verifyToken**(token: String) → `Verify`
- **revokeToken**(refreshToken: String) → `Revoke`
- **createUser**(email: String!, firstName: String!, lastName: String!, password: String!, phone: String, phoneNumber: PhoneNumberInputType!, username: String!) → `CreateUserWithPhoneNumber`
- **addPhoneNumber**(countryCode: String!, number: String!) → `AddPhoneNumber`
- **removePhoneNumber**(phoneId: Int!) → `RemovePhoneNumber`
- **updateUser**(bio: String, firstName: String, lastName: String, profilePicture: String) → `UpdateUser`
- **changePassword**(newPassword: String, oldPassword: String) → `ChangePassword`
- **deleteUser**(password: String) → `DeleteUser`
- **setNotificationRead**(notificationId: Int) → `SetNotificationAsRead`

### CreateChat

```graphql
type CreateChat {

  chat: ChatType
  otherChat: ChatType
}

```

### CreateChatMessage

```graphql
type CreateChatMessage {

  chatMessage: ChatMessageType
}

```

### DeleteChat

```graphql
type DeleteChat {

  success: Boolean
}

```

### UpdateChatMessage

```graphql
type UpdateChatMessage {

  chatMessage: ChatMessageType
}

```

### UnsendChatMessage

```graphql
type UnsendChatMessage {

  success: Boolean
}

```

### DeleteChatMessage

```graphql
type DeleteChatMessage {

  success: Boolean
}

```

### SetChatMessageAsRead

```graphql
type SetChatMessageAsRead {

  chatMessage: ChatMessageType
}

```

### SetChatArchived

```graphql
type SetChatArchived {

  chat: ChatType
}

```

### CreateSelfChat

```graphql
type CreateSelfChat {

  chat: ChatType
}

```

### CreateGroup

```graphql
type CreateGroup {

  userGroup: UserGroupType
}

```

### CreateGroupMessage

```graphql
type CreateGroupMessage {

  message: MessageType
}

```

### CreateGroupMember

```graphql
type CreateGroupMember {

  groupMember: GroupMemberType
}

```

### ChangeAdmin

```graphql
type ChangeAdmin {

  groupMember: GroupMemberType
}

```

### UpdateGroup

```graphql
type UpdateGroup {

  groupCopy: UserGroupMemberCopyType
}

```

### DeleteGroup

```graphql
type DeleteGroup {

  success: Boolean
}

```

### UpdateGroupMessage

```graphql
type UpdateGroupMessage {

  groupMessage: GroupMessageType
}

```

### DeleteGroupMessage

```graphql
type DeleteGroupMessage {

  success: Boolean
}

```

### UnsendGroupMessage

```graphql
type UnsendGroupMessage {

  success: Boolean
}

```

### RemoveGroupMember

```graphql
type RemoveGroupMember {

  success: Boolean
}

```

### LeaveGroup

```graphql
type LeaveGroup {

  success: Boolean
}

```

### RemoveGroup

```graphql
type RemoveGroup {

  success: Boolean
}

```

### SetArchiveGroup

```graphql
type SetArchiveGroup {

  groupCopy: UserGroupMemberCopyType
}

```

### ObtainJSONWebToken

```graphql
type ObtainJSONWebToken {

  payload: GenericScalar!
  refreshExpiresIn: Int!
  token: String!
  refreshToken: String!
}


```

### Refresh

```graphql
"""
The `GenericScalar` scalar type represents a generic
GraphQL scalar value that could be:
String, Boolean, Int, Float, List or Object.
"""
scalar GenericScalar

type Refresh {

  payload: GenericScalar!
  refreshExpiresIn: Int!
  token: String!
  refreshToken: String!
}

```

### Verify

```graphql
type Verify {

  payload: GenericScalar!
}

```

### Revoke

```graphql
type Revoke {

  revoked: Int!
}

```

### CreateUserWithPhoneNumber

```graphql
type CreateUserWithPhoneNumber {

  user: CustomUserType
  phoneNumber: PhoneNumberType
}

input PhoneNumberInputType {
  number: String!
  countryCode: String!
}

```

### AddPhoneNumber

```graphql
type AddPhoneNumber {

  phoneNumber: PhoneNumberType
}

```

### RemovePhoneNumber

```graphql
type RemovePhoneNumber {

  phoneId: Int
}

```

### UpdateUser

```graphql
type UpdateUser {

  user: CustomUserType
}

```

### ChangePassword

```graphql
type ChangePassword {

  user: CustomUserType
}

```

### DeleteUser

```graphql
type DeleteUser {

  userId: Int
}

```

### SetNotificationAsRead

```graphql
type SetNotificationAsRead {

  notification: NotificationType
}
