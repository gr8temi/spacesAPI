from spaces.views import notfound
from django.urls import path, re_path
from .views.auth import login
from .views.add_space import CreateSpace
from .views import agent, customer


urlpatterns = [

    # register other routes here ...
    path('v1/spaces/', CreateSpace.as_view(), name="space"),
    # match route that has not been registered above
    path('v1/auth/login/', login.UserLogin.as_view(), name='login'),
    path('v1/auth/agents/signup/',
         agent.AgentRegister.as_view(), name='agent_register'),
    path('v1/agents/', agent.AgentList.as_view(), name='agents'),
    path('v1/auth/agent/<uuid:agent_id>/',
         agent.AgentDetail.as_view(), name='agent_details'),
    path('v1/auth/customers/signup/',
         customer.CustomerRegister.as_view(), name='customer_register'),
    path('v1/customers/', customer.CustomerList.as_view(), name='customers'),
    path('v1/auth/customer/<uuid:customer_id>/',
         customer.CustomerDetail.as_view(), name='customer_details'),
    # re_path(r'^(?:.*)$', notfound),

]
