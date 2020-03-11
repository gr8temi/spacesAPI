from spaces.views import notfound
from django.urls import path, re_path


urlpatterns = [
    # register other routes here ...

    # match route that has not been registered above
    re_path(r'^(?:.*)$', notfound)
]
