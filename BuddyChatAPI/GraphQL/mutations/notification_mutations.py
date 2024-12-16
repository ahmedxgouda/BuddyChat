import graphene
from graphql_jwt.decorators import login_required
from ..types import NotificationType
from graphene.relay.node import Node

class SetNotificationAsRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.ID()
        
    notification = graphene.Field(NotificationType)
    
    @login_required
    def mutate(self, info, notification_id):
        notification = Node.get_node_from_global_id(info, notification_id)
        notification.is_read = True
        return SetNotificationAsRead(notification=notification)
