from paystackapi.paystack import Paystack
from decouple import config

paystack = Paystack(secret_key=config("PAYSTACK_SECRET_KEY"))
