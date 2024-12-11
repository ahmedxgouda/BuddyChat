import graphene
from ...models import CustomUser, PhoneNumber
from ..types import CustomUserType, PhoneNumberType, PhoneNumberInputType
from ..validators import validate_user_data, validate_phone_number
from graphql_jwt.decorators import login_required
from django.utils import timezone
import bleach
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed
from django.contrib.auth import authenticate

class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()
        
    access_token = graphene.String()
    refresh_token = graphene.String()
    
    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed('Please, enter valid credentials')
        refresh_token = RefreshToken.for_user(user)
        return Login(access_token=str(refresh_token.access_token), refresh_token=str(refresh_token))
    
class Refresh(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String()
        
    access_token = graphene.String()
    refresh_token = graphene.String()
    
    def mutate(self, info, refresh_token):
        try:
            refreshToken = RefreshToken(refresh_token)
            access_token = str(refreshToken.access_token)
            refresh_token = str(refreshToken)
        except TokenError:
            raise InvalidToken('Token is invalid or expired')
        return Refresh(access_token=access_token, refresh_token=refresh_token)
    
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
        cleaner = bleach.sanitizer.Cleaner()
        username = cleaner.clean(username)
        first_name = cleaner.clean(first_name)
        last_name = cleaner.clean(last_name)
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
    class Arguments:
        old_password = graphene.String()
        new_password = graphene.String()
        
    user = graphene.Field(CustomUserType)
    
    @login_required
    def mutate(self, info, old_password, new_password):
        user = info.context.user
        if not user.check_password(old_password):
            raise AuthenticationFailed('Please, enter valid credentials')
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
            raise AuthenticationFailed('Please, enter valid credentials')
        user_id = user.id
        user.delete()
        return DeleteUser(user_id=user_id)
    
class CreateUserWithPhoneNumber(graphene.Mutation):
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
    class Arguments:
        phone_id = graphene.Int(required=True)
        
    phone_id = graphene.Int()
    
    @login_required
    def mutate(self, info, phone_id):
        user = info.context.user
        phone = PhoneNumber.objects.get(pk=phone_id)
        if phone.user != user:
            raise PermissionDenied('You are not authorized to delete this phone number')
        phone.delete()
        return RemovePhoneNumber(phone_id=phone_id)

class AuthMutation(graphene.ObjectType):
    login = Login.Field()
    refresh_token = Refresh.Field()
    create_user = CreateUserWithPhoneNumber.Field()
    add_phone_number = AddPhoneNumber.Field()
    remove_phone_number = RemovePhoneNumber.Field()
    update_user = UpdateUser.Field()
    change_password = ChangePassword.Field()
    delete_user = DeleteUser.Field()

