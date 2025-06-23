from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    A standard pagination class for the entire project.
    """

    page_size = 10  # Default number of items per page
    page_size_query_param = (
        "page_size"  # Allows client to set page size e.g., /api/vendors/?page_size=20
    )
    max_page_size = 100  # Maximum page size the client can request
