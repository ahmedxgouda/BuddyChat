from django.core.exceptions import ValidationError
from .models import CustomUser

def validate_user_data(username, email, password, phone, first_name, last_name):
    
    if CustomUser.objects.filter(username=username).exists():
        raise ValidationError('Username already exists')
    if CustomUser.objects.filter(email=email).exists():
        raise ValidationError('Email already exists')
    if CustomUser.objects.filter(phone=phone).exists():
        raise ValidationError('Phone number already exists')
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if len(phone) != 13:
        raise ValidationError('Phone number must be 13 characters long')
    if len(first_name) < 2:
        raise ValidationError('First name must be at least 2 characters long')
    if len(last_name) < 2:
        raise ValidationError('Last name must be at least 2 characters long')
    return True

def validate_message_content(content):
    if len(content) < 1:
        raise ValidationError('Message content cannot be empty')
    return True