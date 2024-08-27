from rest_framework.pagination import LimitOffsetPagination

from recipes.constants import MAX_LIMIT_PAGINATION, PAGE_SIZE_QUERY_PARAM


class UserPagination(LimitOffsetPagination):
    default_limit = 6
    max_limit = MAX_LIMIT_PAGINATION
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
