from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.v1.user.serializers import UserSerializer
from user.models import User


@method_decorator(cache_page(30), name="get")
class UserListAPIView(ListAPIView):
    """
    WARNING: Caching is applied for performance, under the assumption that the data does not require
    real-time updates. If immediate data freshness is a requirement, pagination should be implemented.
    """

    serializer_class = UserSerializer
    queryset = User.objects.with_entry_summary()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)
