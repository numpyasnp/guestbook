from django.urls import path

from api.v1.user.views import UserListAPIView

urlpatterns = [path("", UserListAPIView.as_view(), name="list-users")]
