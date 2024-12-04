import graphene
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required
from ...models import Notification
from ..types import NotificationType

class SetNotificationAsRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int()
        
    notification = graphene.Field(NotificationType)
    
    @login_required
    def mutate(self, info, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id)
        notification.is_read = True
        return SetNotificationAsRead(notification=notification)
