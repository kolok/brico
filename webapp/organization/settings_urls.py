"""
URL configuration for organization app.
"""

from django.urls import path
from organization.views.settings import (
    OrganizationAuditLibraryDeleteView,
    OrganizationAuditLibraryEditView,
    OrganizationAuditLibraryListView,
    OrganizationEditView,
    OrganizationMemberListView,
    SettingsIndexRedirectView,
)

app_name = "settings"


urlpatterns = [
    path("", SettingsIndexRedirectView.as_view(), name="index"),
    path("organization/<int:pk>/", OrganizationEditView.as_view(), name="organization"),
    path("audits/", OrganizationAuditLibraryListView.as_view(), name="audits"),
    path(
        "audits/<slug:slug>/",
        OrganizationAuditLibraryEditView.as_view(),
        name="audit_library_edit",
    ),
    path(
        "audits/<slug:slug>/delete/",
        OrganizationAuditLibraryDeleteView.as_view(),
        name="audit_library_delete",
    ),
    path("members/", OrganizationMemberListView.as_view(), name="members"),
]
