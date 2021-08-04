# index.py

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models.spaces import Space
from .models.order import Order


@register(Space)
class SpaceIndex(AlgoliaIndex):
    custom_objectID = 'space_id'
    fields = ("agent_id","space_id", "name", "description", "space_type_name", "address", "gmap",
              "number_of_bookings", "capacity", "amount", "agent", "duration", "images", "amenities", "active", "category_name", "city")
    settings = {'searchableAttributes': [
        'name', 'amount', 'availability', 'address', 'space_type', 'gmap', 'capacity', 'category_name']}
    index_name = 'Spaces'


@register(Order)
class BookingIndex(AlgoliaIndex):
    custom_objectID = 'orders_id'
    fields = ("orders_id", "amount", "agent_id", "name", "company_email", "no_of_guest", "extras", "usage_start_date",
              "usage_end_date", "hours_booked", "days_booked", "status", "order_code", "order_type", "space_name", "agent_name", "duration", "images", "user_id", "notes", "space_address", "customer_image")
    settings = {'searchableAttributes': [
        'name',
        'space_name',
        'agent_name',
        'order_code',

    ]}
    index_name = 'Bookings'
