import subscriptions
from spaces.views import home, index, email
from django.urls import path, re_path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # Subscription URLS
    path('subscriptions/', include('subscriptions.urls')),

    # match api index route request
    re_path(r'^(?:api/?)$', index),

    # match test email route
    re_path(r'^test\-email/?$', email),

    # match all api prefixed url requests
    path('api/', include('api.urls')),

    # match all other routes and respond with 403
    re_path(r'^(?:.*)$', home),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
