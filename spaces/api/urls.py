from spaces.views import notfound
from django.urls import path, re_path
from .views.auth import login
from .views.add_space import CreateSpace


from .views.auth import forgot_password, reset_password, verify_email

urlpatterns = [

    # register other routes here ...
    path('spaces/', CreateSpace.as_view(), name="space"),

    # path('auth/login/', login.UserLogin.as_view(), name='login'),
    path('auth/verify-email/', verify_email.VerifyEmail.as_view(), name="verify-email"),
    path('auth/forgot-password/', forgot_password.ForgotPassword.as_view(), name="forgot-password"),
    path('auth/reset-password/', reset_password.ResetPassword.as_view(), name = 'reset-password'),
    re_path(r'^(?:.*)$', notfound),
]
