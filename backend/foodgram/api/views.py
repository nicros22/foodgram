from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   RetrieveModelMixin,
                                   UpdateModelMixin)
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ViewSetMixin, ReadOnlyModelViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from .filters import IngredientFilter
from .serializers import (
    TokenCreateSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserAvatarSetSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscribeSerializer)
from .paginators import UserPagination
from recipes.models import Tag, Ingredient
from users.models import Follow


User = get_user_model()


class GetTokenView(GenericAPIView):
    serializer_class = TokenCreateSerializer
    #permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])
        if user:
            access = AccessToken.for_user(user)
            return Response({'auth_token': str(access)}, status=status.HTTP_200_OK)
        return Response({'message': 'Wrong credentials'}, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class UserViewSet(CreateModelMixin,
                  ListModelMixin,
                  RetrieveModelMixin,
                  ViewSetMixin,
                  GenericAPIView):
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'list']:
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            serializer.save()
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='me/avatar', methods=['put', 'delete'])
    def avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSetSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='me', methods=['get'])
    def me(self, request):
        try:
            user = self.get_queryset().get(id=request.user.id)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.get_queryset().model.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def set_password(self, request, *args, **kwargs):
        user = request.user
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'password changed'}, status=status.HTTP_204_NO_CONTENT)\


    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {"detail": "You are already following this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {"detail": "You cannot subscribe to yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
