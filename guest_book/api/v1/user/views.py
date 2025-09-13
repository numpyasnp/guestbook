from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView

from api.v1.user.serializers import UserSerializer
from user.models import User


@method_decorator(cache_page(60 * 5), name="get")
class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.with_entry_summary()
