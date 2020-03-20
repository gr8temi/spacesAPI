from spaces.views import notfound
from django.urls import path, re_path

from .views.spaces import Spaces,SpacesDetail

urlpatterns = [
    # register other routes here ...

    # match route that has not been registered above
    re_path(r'^(?:.*)$', notfound),
    path("spaces/",Spaces.as_view(), name="spaces"),
    path("space/<int:spaceId>",SpacesDetail.as_view(), name="space_detail"),
]
