from spaces.views import notfound
from django.urls import path, re_path
from .views.auth import login

urlpatterns = [
    # register other routes here ...
    # match route that has not been registered above
    path('auth/login/', login.UserLogin.as_view(), name='login'),
    # re_path(r'^(?:.*)$', notfound),
]
