from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from ..models.order import Order
from ..models.user import User
from decouple import config
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from ..consumers.channel_layers import notification_creator
from ..signals import subscriber


class PaystackHooks(APIView):
    def post(self, request, format=None):
        data = request.data
        event = data.get('event')
        paystack_data = data.get("data")
        bookings = Order.objects.filter(transaction_code=paystack_data.get("reference"))
        order = bookings.first()
        customer_email = order.user.email
        order_code = order.order_code
        agent = order.space.agent
        agent_mail = agent.user.email
        agent_name = agent.user.name
        customer_name = order.name
        space = order.space
        sender = config(
            "EMAIL_SENDER", default="space.ng@gmail.com")
        if event == "charge.success":
            for booking in bookings:
                booking.status = "booked"
                booking.save()
            space.number_of_bookings +=1
            space.save()
            # notifications

            # notification for customer booking space
            subject_customer = "BOOKING COMPLETE"
            to_customer = customer_email
            # customer_content = f"Dear {to_customer}, your Booking has been completed"

            # notification for agent that registered space
            subject_agent = "YOU HAVE A BOOKING"
            to_agent = agent_mail
            # agent_content = f"Dear {agent_name}, you have a booking placed for your space {space.name} listed on our platform."
            
            #notification for admin about customer booking space
            subject_admin = "A NEW BOOKING HAS BEEN MADE"
            all_admin = User.objects.filter(is_super=True)
            admin_email_list = [admin.email for admin in all_admin if all_admin]

            guest_template = get_template('api/order/customer_booking_notification.html')
            guest_content = guest_template.render({'guest_name': customer_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
            msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
            msg.attach_alternative(guest_content, "text/html")
            msg.send()
            
            host_template = get_template('api/order/space_host_booking_notification.html')
            host_content = host_template.render({'host_name': agent_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
            msg = EmailMultiAlternatives(subject_agent, host_content, sender, to=[to_agent])
            msg.attach_alternative(host_content, "text/html")
            msg.send()

            admin_template = get_template('api/admin/booking_alert.html')
            admin_content = admin_template.render({"login_url": f"{config('FRONTEND_URL')}/signin"})
            msg = EmailMultiAlternatives(subject_admin, admin_content, sender, to=admin_email_list)
            msg.attach_alternative(admin_content, "text/html")
            msg.send()

            subscriber.connect(notification_creator)
            subscriber.send(sender=self.__class__,
                            data={"user_id": f"{agent.user.user_id}", "notification": f"You have a new booking {order_code} "})
            return Response({"message": "done"}, status=status.HTTP_200_OK)
        else:
            for booking in bookings:
                booking.status = "failed"
                booking.save()
            subject_customer = "BOOKING PAYMENT FAILED"
            to_customer = customer_email
            guest_template = get_template('api/order/customer_booking_payment_failed.html')
            guest_content = guest_template.render({'guest_name': customer_name, "login_url": f"{config('FRONTEND_URL')}/signin", "space_name":space.name, "space_location":space.address })
            msg = EmailMultiAlternatives(subject_customer, guest_content, sender, to=[to_customer])
            msg.attach_alternative(guest_content, "text/html")
            msg.send()
            return Response({"message": "failed"}, status=status.HTTP_200_OK)
            