import graphene
from ...models import CustomUser, PhoneNumber
from ..types import CustomUserType, PhoneNumberType, PhoneNumberInputType
from ..validators import validate_user_data, validate_phone_number
from graphql_jwt.decorators import login_required
from django.utils import timezone
import bleach
from django.core.exceptions import PermissionDenied
from graphql_jwt import ObtainJSONWebToken, Refresh, Verify, Revoke
from ..helpers import get_node_or_error
class CreateUser(graphene.Mutation):
    """Mutation to create a user. Deprecated"""
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
        cleaner = bleach.sanitizer.Cleaner()
        username = cleaner.clean(username)
        first_name = cleaner.clean(first_name)
        last_name = cleaner.clean(last_name)
        user = CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone, first_name=first_name, last_name=last_name)
        user.save()
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    """Mutation to update the current user's data"""
    class Arguments:
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        profile_picture = graphene.String(required=False)
        bio = graphene.String(required=False)
        
    user = graphene.Field(CustomUserType)
    
    @login_required
    def mutate(self, info, first_name=None, last_name=None, profile_picture=None, bio=None):
        user = info.context.user
        cleaner = bleach.sanitizer.Cleaner()
        if first_name:
            user.first_name = cleaner.clean(first_name)
        if last_name:
            user.last_name = cleaner.clean(last_name)
        if profile_picture:
            user.profile_pic = cleaner.clean(profile_picture)
        if bio:
            user.bio = cleaner.clean(bio)
            user.updated_at = timezone.now()
        user.save()
        return UpdateUser(user=user)
    
class ChangePassword(graphene.Mutation):
    """Mutation to change the current user's password"""
    class Arguments:
        old_password = graphene.String()
        new_password = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    @login_required
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise PermissionDenied('Please, enter valid credentials')
        user.set_password(new_password)
        user.save()
        return ChangePassword(user=user)

class DeleteUser(graphene.Mutation):
    """Mutation to delete the current user"""
    class Arguments:
        password = graphene.String()
    
    user_id = graphene.Int()
    @login_required
    def mutate(self, info, password):
        user = info.context.user
        if not user.check_password(password):
            raise PermissionDenied('Please, enter valid credentials')
        user_id = user.id
        user.delete()
        return DeleteUser(user_id=user_id)
    
class CreateUserWithPhoneNumber(graphene.Mutation):
    """Mutation to create a user with a phone number"""
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        phone_number = PhoneNumberInputType(required=True)
        phone = graphene.String(required=False)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        
    user = graphene.Field(CustomUserType)
    phone_number = graphene.Field(PhoneNumberType)
    
    def mutate(self, info, username, email, password, phone_number, first_name, last_name, phone=None):
        validate_phone_number(phone_number.number, phone_number.country_code)
        validate_user_data(username, email, password, phone_number.number, first_name, last_name)
        if phone:
            validate_phone_number(phone)
        cleaner = bleach.sanitizer.Cleaner()
        username = cleaner.clean(username)
        first_name = cleaner.clean(first_name)
        last_name = cleaner.clean(last_name)
        user = CustomUser.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, phone=phone)
        user.save()
        phone = PhoneNumber.objects.create(number=phone_number.number, country_code=phone_number.country_code, user=user)
        phone.save()
        return CreateUserWithPhoneNumber(user=user, phone_number=phone)

class AddPhoneNumber(graphene.Mutation):
    """Mutation to add a phone number to the current user"""
    class Arguments:
        number = graphene.String(required=True)
        country_code = graphene.String(required=True)
        
    phone_number = graphene.Field(PhoneNumberType)
    
    @login_required
    def mutate(self, info, number, country_code):
        validate_phone_number(number, country_code)
        user = info.context.user
        phone = PhoneNumber.objects.create(number=number, country_code=country_code, user=user)
        phone.save()
        return AddPhoneNumber(phone_number=phone)

class RemovePhoneNumber(graphene.Mutation):
    """Mutation to remove a phone number from the current user"""
    class Arguments:
        phone_id = graphene.ID(required=True)
        
    success = graphene.Boolean()
    
    @login_required
    def mutate(self, info, phone_id):
        phone = get_node_or_error(info, phone_id)
        user = info.context.user
        if phone.user != user:
            raise PermissionDenied('You are not authorized to delete this phone number')
        phone.delete()
        return RemovePhoneNumber(success=True)

class AuthMutation(graphene.ObjectType):
    """The Auth Mutation for the GraphQL API"""
    login = ObtainJSONWebToken.Field(description="Login to the API. Returns a token")
    refresh_token = Refresh.Field(description="Refresh the token")
    verify_token = Verify.Field(description="Verify the token")
    revoke_token = Revoke.Field(description="Revoke the token")
    create_user = CreateUserWithPhoneNumber.Field(description="Create a user with a phone number")
    add_phone_number = AddPhoneNumber.Field(description="Add a phone number to the current user")
    remove_phone_number = RemovePhoneNumber.Field(description="Remove a phone number from the current user")
    update_user = UpdateUser.Field(description="Update the current user's data")
    change_password = ChangePassword.Field(description="Change the current user's password")
    delete_user = DeleteUser.Field(description="Delete the current user")

