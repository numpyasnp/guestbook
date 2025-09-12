from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class GuestBookPagination(PageNumberPagination):
    page_size = 3

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
                "total_pages": math.ceil(self.page.paginator.count / self.get_page_size(self.request)),
                "current_page_number": self.page.number,
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "entries": data,
            }
        )
