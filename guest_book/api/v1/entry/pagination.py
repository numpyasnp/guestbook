from django.core.cache import cache
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class EntryPagination(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        cache_key = "entry_count"
        total_count = cache.get(cache_key)
        if total_count is None:
            total_count = self.page.paginator.count
            cache.set(cache_key, total_count, timeout=300)

        return Response(
            {
                "count": total_count,
                "page_size": self.get_page_size(self.request),
                "total_pages": math.ceil(total_count / self.get_page_size(self.request)),
                "current_page_number": self.page.number,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "entries": data,
            }
        )
