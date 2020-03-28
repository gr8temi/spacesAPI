from spaces.views import notfound
from django.urls import path, re_path
from .views.auth import login
from .views.add_space import CreateSpace



urlpatterns = [

    # register other routes here ...
    path('spaces/', CreateSpace.as_view(), name="space"),

    # match route that has not been registered above
    path('auth/login/', login.UserLogin.as_view(), name='login'),
    # re_path(r'^(?:.*)$', notfound),
]
