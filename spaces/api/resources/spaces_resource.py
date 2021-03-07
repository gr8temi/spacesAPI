from import_export import resources
from ..models.spaces import Space


class SpaceResource(resources.ModelResource):
    class Meta:
        model = Space
        exclude = ("gmap",
                   "images",
                   "objects",
                   "created_at",
                   "updated_at",
                   "image_details",
                   )

