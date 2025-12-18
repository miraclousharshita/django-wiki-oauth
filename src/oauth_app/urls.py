from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(  # type: ignore[arg-type]
    path("admin/", admin.site.urls),
    path("", include("user_profile.urls")),
)
