from rest_framework.permissions import BasePermission
from ..models.user import User

def is_user(user_id):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None

class UserIsAnAgent(BasePermission):

    def has_permission(self,request,view):
        user_id = request.user.id
        is_valid_user = is_user(user_id)
        if is_valid_user is not None:
            is_agent = is_valid_user.is_agent
            if is_agent:
                return True
            else:
                return False
        else:
            return False