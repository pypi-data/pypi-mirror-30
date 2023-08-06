from django.urls import path
from django.conf import settings

if settings.DJANGO_ADDON_ENABLE_GIS:
    from django.contrib.gis import admin
else:
    from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
]
