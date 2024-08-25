from django.contrib import admin
from django.urls import include, path

from api.views import get_recipe

urlpatterns = [
    path('s/<str:short_link>/', get_recipe),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
