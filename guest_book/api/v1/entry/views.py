from rest_framework.generics import ListCreateAPIView

from api.v1.entry.pagination import EntryPagination
from api.v1.entry.serializers import EntryCreateSerializer, EntryResponseSerializer
from entry.models import Entry


class EntryCreateListAPIView(ListCreateAPIView):
    queryset = Entry.objects.select_related("user").order_by("created_date")
    pagination_class = EntryPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EntryCreateSerializer
        return EntryResponseSerializer
