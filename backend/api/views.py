from django.contrib.auth import authenticate
from django.db.models import Count, Sum
from django.http.response import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (ModelViewSet, ReadOnlyModelViewSet,
                                     ViewSetMixin)
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import UserPagination
from api.permissions import AuthorPermission
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeInfoSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             TagSerializer, TokenCreateSerializer,
                             UserAvatarSetSerializer, UserCreateSerializer,
                             UserSerializer)
from api.utils.create_short_link import create_short_link
from api.utils.generate_shopping_list import (generate_pdf,
                                              generate_shopping_list)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, ShortLink, Tag)
from users.models import Follow, User


class AddRemoveMixin:
    def add_remove(self, request, pk, model,
                   serializer_class,
                   success_message,
                   error_message):
        instance = get_object_or_404(Recipe, id=pk)
        if request.method == 'DELETE':
            try:
                obj = model.objects.get(user=request.user, recipe_id=pk)
            except model.DoesNotExist:
                return Response({"detail": error_message},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'user': request.user.id, 'recipe': instance.id}
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetTokenView(GenericAPIView):
    serializer_class = TokenCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])
        if user:
            access = AccessToken.for_user(user)
            return Response({'auth_token': str(access)},
                            status=status.HTTP_200_OK)
        return Response({'message': 'Wrong credentials'},
                        status=status.HTTP_400_BAD_REQUEST)


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
    queryset = User.objects.all().annotate(
        recipes_count=Count('recipes')
    )
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def set_password(self, request, *args, **kwargs):
        user = request.user
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'password changed'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if Follow.objects.filter(user=request.user,
                                     author=author).exists():
                return Response(
                    {"detail": "You are already following this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user == author:
                return Response(
                    {"detail": "You cannot subscribe to yourself."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=request.user, author=author)
            serializer = SubscribeSerializer(author,
                                             context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Follow.objects.filter(user=request.user,
                                             author=author).first()
        if not subscription:
            return Response(
                {"detail": "Subscription does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(queryset, many=True,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(ModelViewSet, AddRemoveMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (AuthorPermission,)
    pagination_class = UserPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeInfoSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if (
            self.action in [
                'favorite',
                'shopping_cart',
                'download_shopping_cart',
                'create',
                'update'
            ]
        ):
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (AuthorPermission,)
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[AuthorPermission])
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = generate_shopping_list(ingredients)
        pdf_buffer = generate_pdf(shopping_list)

        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename='shopping_list.pdf',
            content_type='application/pdf'
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        get_object_or_404(Recipe, pk=kwargs["pk"])
        link = create_short_link(kwargs["pk"])
        link = f'{request.META["HTTP_HOST"]}/s/{link}'
        return Response(status=status.HTTP_200_OK, data={"short-link": link})

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_remove(
            request, pk, Favorite, FavoriteSerializer,
            success_message="Recipe added to favorites.",
            error_message="Recipe not in favorites."
        )

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.add_remove(
            request, pk, ShoppingCart, ShoppingCartSerializer,
            success_message="Recipe added to shopping cart.",
            error_message="Recipe not in shopping cart."
        )


@api_view(['GET'])
def get_recipe(request, short_link):
    link = get_object_or_404(ShortLink, link=short_link)
    return redirect(
        f'https://{request.META["HTTP_HOST"]}/recipes/{link.recipe_id}/')
