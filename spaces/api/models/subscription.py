from django.db import models
import uuid
from datetime import datetime, timedelta
SUBSCRIPTION_CHOICES = [
    ("monthly", "Monthly"),
    ("quarterly", "Quarterly"),
    ("bi-annually", "Bi-annually"),
    ("yearly", "Yearly"),
    ("per minute", "Per Minute")
]
SUBSCRIPTION_PLANS = [
    ("basic", "Basic"),
    ("standard", "Standard"),
    ("premium", "Premium")
]


class SubscriptionManager(models.Manager):
    def minute_subscription(self, start_time):
        return start_time + timedelta(minutes=1)

    def monthly_subscription(self, start_time):
        return start_time + timedelta(days=31)

    def quarterly_subscription(self, start_time):
        return start_time + timedelta(days=91)

    def bi_annual_subscription(self, start_time):
        return start_time + timedelta(days=183)

    def annual_subscription(self, start_time):
        if start_time.month > 2 and bool((start_time.year+1) % 4 == 0):
            return start_time + timedelta(days=366)
        elif start_time.month > 2 and bool((start_time.year+1) % 4 != 0):
            return start_time + timedelta(days=365)
        elif start_time.month <= 2 and bool((start_time.year) % 4 != 0):
            return start_time + timedelta(days=365)
        elif start_time.month <= 2 and bool((start_time.year) % 4 == 0):
            return start_time + timedelta(days=366)


class Subscription(models.Model):

    subscription_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    subscription_title = models.CharField(max_length=50, default="Package")
    subscription_type = models.CharField(
        max_length=12, choices=SUBSCRIPTION_CHOICES, default="monthly")
    subscription_plan = models.CharField(
        max_length=12, choices=SUBSCRIPTION_PLANS, default="basic")
    cost = models.IntegerField()

    def __str__(self):
        return self.subscription_title

    def subscription_name(self):
        return self.subscription_title


class SubscriptionPerAgent(models.Model):
    sub_per_agent_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    recurring = models.BooleanField(default=False)
    next_due_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(
        auto_now=False, auto_now_add=False, blank=True, null=True)
    is_cancelled = models.BooleanField(default=False)
    reference_code = models.CharField(max_length=50, blank=True, unique=True)
    agent = models.ForeignKey("api.Agent", verbose_name='Space Host Business Name', on_delete=models.CASCADE, null=True)
    authorization_code = models.CharField(max_length=50, blank=True)
    amount = models.IntegerField(default=0)
    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'subscription per space host'
        verbose_name_plural = 'Subscriptions per space host'

    def subscription_name(self):
        return self.subscription.subscription_title
    
    def subscription_plan(self):
        return self.subscription.subscription_plan

    def subscription_type(self):
        return self.subscription.subscription_type

    def space_host(self):
        return self.agent.user.name

    def __str__(self):
        return self.agent.user.name


class BillingHistory(models.Model):

    billing_history_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(verbose_name='Space Host', max_length=50)
    agent_email = models.EmailField(verbose_name='Space Host Email Address' , max_length=254)
    payment_cost = models.IntegerField()
    payment_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    next_due_date = models.DateTimeField(auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name_plural = 'Billing histories'
