from decouple import config
from django.http import JsonResponse
from django.core.mail import send_mail


def home(request):
    message = 'You are not expected to be here, visit /api'
    return JsonResponse(dict(message=message), status=403)

def index(request):
    message = 'Welcome to 234Spaces Rest API'
    return JsonResponse(dict(message=message))

def email(request):
    sender = config('EMAIL_SENDER', default="dummy@gmail.com")
    recipient = [config('TEST_EMAIL_RECIPIENT', default="dummy@gmail.com")]
    subject = 'Testing email settings'
    message = 'Testing email settings - <a href="http://example.com">Example Link</a>'
    status = send_mail(subject, message, sender, recipient, html_message=message)
    return JsonResponse(dict(status=status, sender=sender, recipient=recipient[0]))

def notfound(request):
    message = 'Route provided was not found'
    return JsonResponse(dict(message=message), status=404)
