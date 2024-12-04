from graphql_jwt import Verify, Refresh, ObtainJSONWebToken
from graphql_jwt.exceptions import JSONWebTokenError
import graphene
from ...models import CustomUser
from ..types import CustomUserType
from ..validators import validate_user_data

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

class AuthMutation(graphene.ObjectType):
    token_auth = ObtainJSONWebTokenCustom.Field()
    verify_token = Verify.Field()
    refresh_token = Refresh.Field()
    create_user = CreateUser.Field()
