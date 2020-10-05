import random
import string
import re
from rest_framework import status
from django.core.mail import send_mail
from decouple import config
from rest_framework.response import Response


#This function generates 8 random alphanumeric characters
def random_string_generator(size=8, chars=string.ascii_lowercase + string.digits+ string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))    

# This function validate len of value if is greather than num
def validate_len(value, num):
    return True if len(value) < num else False

# This regex checks if email is valid
email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

# This regex checks if a word starts with alphabet, must not contain space, and other characters except underscore and hyphen
username_regex = '^([a-zA-Z])[a-zA-Z_-]*[\w_-]*[\S]$|^([a-zA-Z])[0-9_-]*[\S]$|^[a-zA-Z]*[\S]$'

def regex_validator(value, regex):
    if not value:
        return False
    else:
        return bool(re.search(regex, value))

# This funciton checks if the value is empty 
def check_empty_value(value):
    return bool(value)

def customer_message(data):
    return {
    "first_name":data['first_name'],
    "last_name":data['last_name'],
    "user_name":data['user_name'].strip(),
    "email":data['email'],
}

def agent_message(data):
    return {
    "shop_name":data['shop_name'],
    "user_name":data['user_name'].strip(),
    "email":data['email'],
    "email_verified": False,
    "account_verified": False
}

def send_email(message_details):
    try:
        send_mail(
            subject=message_details['subject'], 
            message=message_details["html_content"],
            from_email=message_details['from_email'],
            recipient_list=message_details['to'], 
            html_message=message_details['link_message'],
        )
        return True
    except Exception as Error:
        return False
