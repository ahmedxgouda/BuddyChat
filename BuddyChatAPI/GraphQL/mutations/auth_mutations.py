from graphql_jwt import Verify, Refresh, ObtainJSONWebToken
from graphql_jwt.exceptions import JSONWebTokenError
import graphene
from ...models import CustomUser
from ..types import CustomUserType
from ..validators import validate_user_data
from graphql_jwt.decorators import login_required
from django.utils import timezone

class ObtainJSONWebTokenCustom(ObtainJSONWebToken):
    @classmethod
    def resolve(cls, root, info, **kwargs):
        response = super().resolve(root, info, **kwargs)
        user = info.context.user
        if not user.is_authenticated:
            raise JSONWebTokenError('Please, enter valid credentials')
        # if not EmailAddress.objects.filter(user=user, verified=True).exists():
        #     raise JSONWebTokenError('Please, verify your email address')
        return response
    
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        phone = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    def mutate(self, info, username, email, password, phone, first_name, last_name):
        validate_user_data(username, email, password, phone, first_name, last_name)
        user = CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone, first_name=first_name, last_name=last_name)
        user.save()
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        profile_picture = graphene.String(required=False)
        bio = graphene.String(required=False)
        
    user = graphene.Field(CustomUserType)
    
    @login_required
    def mutate(self, info, first_name, last_name, profile_picture, bio):
        user = info.context.user
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_pic = profile_picture
        if bio:
            user.bio = bio
            user.updated_at = timezone.now()
        user.save()
        return UpdateUser(user=user)
    
class ChangePassword(graphene.Mutation):
    class Arguments:
        old_password = graphene.String()
        new_password = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    @login_required
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise JSONWebTokenError('Please, enter valid credentials')
        user.set_password(new_password)
        user.save()
        return ChangePassword(user=user)

class DeleteUser(graphene.Mutation):
    class Arguments:
        password = graphene.String()
    
    user_id = graphene.Int()
    @login_required
    def mutate(self, info, password):
        user = info.context.user
        if not user.check_password(password):
            raise JSONWebTokenError('Please, enter valid credentials')
        user_id = user.id
        user.delete()
        return DeleteUser(user_id=user_id)

class AuthMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebTokenCustom.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    change_password = ChangePassword.Field()
    delete_user = DeleteUser.Field()

