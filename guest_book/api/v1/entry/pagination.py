from django.core.cache import cache
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class EntryPagination(PageNumberPagination):
    """
    Custom pagination for GuestBook entries.

    Note:
    PageNumberPagination may slow down on large datasets
    due to OFFSET cost. CursorPagination is recommended
    for better performance in production.
    """

    page_size = 3

    def get_paginated_response(self, data):
        cache_key = "entry_count"
        total_count = cache.get(cache_key)
        if total_count is None:
            total_count = self.page.paginator.count
            cache.set(cache_key, total_count, timeout=30)
            # Note: Count is cached with a short TTL.
            # Immediate consistency is not guaranteed; newly added entries may not appear in the count instantly.

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
