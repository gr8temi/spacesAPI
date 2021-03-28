from import_export import resources
from api.models.favourite import Favourite

class FavouriteResource(resources.ModelResource):
    class Meta:
        model = Favourite
