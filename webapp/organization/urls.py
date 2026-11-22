"""
URL configuration for organization app.
"""

from django.urls import path
from organization.views.organization import (
    OrganizationCreateView,
    OrganizationSwitchView,
)

app_name = "organization"

urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="create"),
    path(
        "switch/<int:organization_id>/", OrganizationSwitchView.as_view(), name="switch"
    ),
]
