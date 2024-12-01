import graphene
from .types import CustomUserType, ChatType, UserGroupType

class CustomUserConnection(graphene.relay.Connection):
    class Meta:
        node = CustomUserType
        
class ChatConnection(graphene.relay.Connection):
    class Meta:
        node = ChatType
        
class UserGroupConnection(graphene.relay.Connection):
    class Meta:
        node = UserGroupType
        
