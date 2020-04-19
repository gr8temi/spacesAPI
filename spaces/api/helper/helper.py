import random
import string
from django.core.mail import send_mail

# This function generates 8 random alphanumeric characters
def random_string_generator(size=8, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

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
        return Error

def order_code(size=6, chars=string.digits):
    digit = ''.join(random.choice(chars) for _ in range(size))
    code = f"234Spaces-{digit}"
    return code
