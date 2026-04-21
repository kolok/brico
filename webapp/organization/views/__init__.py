"""
Views package for the organization app.

This module re-exports commonly used views for backwards compatibility,
so existing imports like ``from organization.views import ...`` keep working.
"""

from .organization import OrganizationCreateView, OrganizationSwitchView
from .settings import OrganizationAuditLibraryListView, OrganizationEditView

__all__ = [
    "OrganizationCreateView",
    "OrganizationSwitchView",
    "OrganizationEditView",
    "OrganizationAuditLibraryListView",
]
