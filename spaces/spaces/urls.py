from .views import home, index, email
from django.urls import path, re_path, include

urlpatterns = [
    # match api index route request
    # re_path(r'^(?:api/?)$', index),

    # match test email route
    re_path(r'^test\-email/?$', email),

    # match all api prefixed url requests
    path('api/', include('api.urls')),

    # match all other routes and respond with 403
    # re_path(r'^(?:.*)$', home)    
]
