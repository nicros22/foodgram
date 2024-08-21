from rest_framework.pagination import LimitOffsetPagination


class UserPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 100
    page_size_query_param = 'limit'