from django.urls import include, path

from . import api_views, views

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("vue/", views.vue_app, name="vue-app"),  # Add this line
    path("search", views.search_articles, name="search"),
    path("accounts/login", views.login_oauth, name="login"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("", views.index),
    path("api/user/", api_views.UserInfoAPIView.as_view(), name="api-user"),
    path("api/stats/", api_views.WikiStatsAPIView.as_view(), name="api-stats"),
    path("api/search/", api_views.SearchAPIView.as_view(), name="api-search"),
]
