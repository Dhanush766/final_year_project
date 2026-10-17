"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

from employees.views import AppLoginView, AppLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("", include("employees.urls")),
]
