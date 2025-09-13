from rest_framework.generics import ListAPIView

from api.v1.user.serializers import UserSerializer
from user.models import User


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.with_entry_summary()
