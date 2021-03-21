from decouple import config
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

class CancellationActions:

    def __init__(self, cancellation):
        self.cancellation = cancellation
        self.host_email = self.cancellation.agent.user.email
        self.guest_email = self.cancellation.customer.user.email
        self.host_name = self.cancellation.agent.user.name
        self.guest_name = self.cancellation.customer.user.name
        self.space_name = self.cancellation.booking.space.name
        self.space_location = self.cancellation.booking.space.address
        self.reason_for_cancellation = self.cancellation.reason
        self.subject = 'Booking Cancellation Status'

    def send_approval_email(self):
        guest_template = get_template('api/cancellation_email_templates/approval_notification_guest.html')
        guest_content = guest_template.render({'guest_name': self.guest_name, 'space_name': self.space_name, 'space_location': self.space_location, 'reason': self.reason_for_cancellation})
        msg = EmailMultiAlternatives(self.subject, guest_content, config('EMAIL_SENDER'), to=[self.guest_email])
        msg.attach_alternative(guest_content, "text/html")
        msg.send()
        
        host_template = get_template('api/cancellation_email_templates/approval_notification_host.html')
        host_content = host_template.render({'host_name': self.host_name, 'space_name': self.space_name, 'space_location': self.space_location})
        msg = EmailMultiAlternatives(self.subject, host_content, config('EMAIL_SENDER'), to=[self.host_email])
        msg.attach_alternative(host_content, "text/html")
        msg.send()
        
    def send_decline_email(self):
        guest_template = get_template('api/cancellation_email_templates/decline_notification_guest.html')
        guest_content = guest_template.render({'guest_name': self.guest_name, 'space_name': self.space_name, 'space_location': self.space_location, 'reason': self.reason_for_cancellation})
        msg = EmailMultiAlternatives(self.subject, guest_content, config('EMAIL_SENDER'), to=[self.guest_email])
        msg.attach_alternative(guest_content, "text/html")
        msg.send()
