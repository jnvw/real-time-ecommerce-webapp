from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse

urlpatterns = [
    path("health/", lambda r: HttpResponse("OK"), name="health"),
    path('admin/', admin.site.urls),
    # Include the new dashboard URLs
    path('', include('dashboard.urls')),
    path('', include('shop.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
