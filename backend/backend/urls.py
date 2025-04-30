from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("login_and_register.urls")),
    path("api/", include("ai_recommender.urls")),
    path("api/", include("vendor.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
