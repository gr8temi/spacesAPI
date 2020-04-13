# index.py

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models.spaces import Space


@register(Space)
class SpaceIndex(AlgoliaIndex):
    custom_objectID = 'space_id'
    settings = {'searchableAttributes': [
        'name', 'price', 'availability', 'location']}
    index_name = 'Spaces'
