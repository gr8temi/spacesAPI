# from .spaces.views import notfound
from django.urls import path, re_path, include
from rest_framework import routers
from .views.agent_views import AgentList, AgentDetail, AgentRegister
from .views.user_views import UserList, UserDetail
from .views.agent_views import AgentDetail, AgentList
from .views.space_views import SpaceDetail, SpaceEdit
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views.auth import login


urlpatterns = [
    # register other routes here ...
    path('v1/agents', AgentList.as_view()),
    path('auth/login/', login.UserLogin.as_view(), name='login'),
    path('v1/users/', UserList.as_view()),
    path('v1/user/<uuid:user_id>', UserDetail.as_view()),
    path('v1/agents/', AgentList.as_view(), name='all_agents'),
    path('v1/agent/<uuid:agent_id>', AgentDetail.as_view()),
    path('v1/agents/register', AgentRegister.as_view(), name='register-agent' ),
    path('v1/spaces/', SpaceDetail.as_view()),
    path('v1/spaces/edit/<uuid:space_id>', SpaceEdit.as_view()),
    # match route that has not been registered above
    # re_path(r'^(?:.*)$', notfound)
]


urlpatterns = format_suffix_patterns(urlpatterns)
