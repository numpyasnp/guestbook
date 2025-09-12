from django.urls import path

from api.v1.entry.views import EntryCreateListAPIView

app_name = "entry"


urlpatterns = [path("", EntryCreateListAPIView.as_view(), name="entry-list-create")]
