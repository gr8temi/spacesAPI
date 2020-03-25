from spaces.views import notfound
from django.urls import path, re_path

from .views.auth import login, forgot_password, reset_password

urlpatterns = [
    # register other routes here ...

    # match route that has not been registered above
    re_path(r'^(?:.*)$', notfound),

    path('auth/login/', login.UserLogin.as_view(), name='login'),
    path('auth/forgot_password/', forgot_password.ForgotPassword.as_view(), name='forgot_password'),
    path('auth/reset_password/', reset_password.ResetPassword.as_view(), name = 'reset_password')
]
