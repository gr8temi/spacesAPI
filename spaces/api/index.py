# index.py

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models.spaces import Space
from .models.order import Order


@register(Space)
class SpaceIndex(AlgoliaIndex):
    custom_objectID = 'space_id'
    settings = {'searchableAttributes': [
        'name', 'amount', 'availability', 'address', 'space_type', 'gmap', 'capacity']}
    index_name = 'Spaces'


@register(Order)
class BookingIndex(AlgoliaIndex):
    custom_objectID = 'orders_id'
    settings = {'searchableAttributes': [
        'name',
        'space_name',
        'agent_name',
        'order_code',

    ]}
    index_name = 'Bookings'
