# pagination.py

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to return the pagination response with the 'next', 'previous', 
    'count', and 'results' keys.
    """
    page_size = 20  # Set default page size
    page_size_query_param = 'page_size'  # Allow clients to specify a custom page size
    max_page_size = 100  # Limit the maximum page size to 100 items

    def get_paginated_response(self, data):
        """
        Return a custom response that includes pagination metadata.
        """
        return Response({
            'links': {
                'next': self.get_next_link(),  # Link to the next page
                'previous': self.get_previous_link()  # Link to the previous page
            },
            'count': self.page.paginator.count,  # Total number of items
            'results': data  # The serialized data for the current page
        })
