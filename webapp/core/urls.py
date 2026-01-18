"""
URL configuration for core project.
"""

from core.views import DashboardView, IndexView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("audits/", include(("audits.urls", "audits"), namespace="audits")),
    path(
        "organizations/",
        include(("organization.urls", "organization"), namespace="organization"),
    ),
    # Auth interface
    path("accounts/", include("allauth.urls")),
    # Include the API endpoints
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
]

# Django Debug Toolbar - only active in DEBUG mode
if settings.DEBUG:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
