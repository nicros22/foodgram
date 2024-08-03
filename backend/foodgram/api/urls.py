from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users',)
router.register('tags',)
router.register('recipes',)
router.register('ingredients',)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]