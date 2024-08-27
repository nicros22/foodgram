from rest_framework.pagination import PageNumberPagination

from recipes.constants import (DEFAULT_LIMIT_PAGINATION, MAX_LIMIT_PAGINATION,
                               PAGE_SIZE_QUERY_PARAM)


class UserPagination(PageNumberPagination):
    default_limit = DEFAULT_LIMIT_PAGINATION
    max_limit = MAX_LIMIT_PAGINATION
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
