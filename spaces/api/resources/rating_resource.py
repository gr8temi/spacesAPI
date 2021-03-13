from import_export import resources
from api.models.ratings import Rating

class RatingResource(resources.ModelResource):
    class Meta:
        model = Rating
