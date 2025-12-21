"""
Views for core application.
"""

from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY, ORGANIZATIONS_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView
from organization.permissions import check_organization_permission


class IndexView(TemplateView):
    """View for the home page. Redirects authenticated users to dashboard."""

    template_name = "index.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


# FIXME :should we keep the dashboard here or move it to audit app?
class DashboardView(LoginRequiredMixin, TemplateView):
    """View for the dashboard page (authenticated users only)."""

    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirect to organization creation if user has no organizations."""
        # Check organizations before calling super().dispatch() to avoid rendering
        # the template unnecessarily. LoginRequiredMixin will handle authentication
        # check and redirect unauthenticated users to login.
        if request.user.is_authenticated:
            # Check if user has organizations
            if not request.session.get(ORGANIZATIONS_SESSION_KEY, []):
                return redirect("organization:create")

            # Check if user has a current organization selected
            organization_id = request.session.get(
                CURRENT_ORGANIZATION_SESSION_KEY, [None]
            )[0]
            if organization_id is None:
                raise PermissionDenied("No organization selected")

            # Check if user has rights on the current organization
            # Using view_project as a base permission to verify membership
            # Type ignore: request.user is guaranteed to be authenticated at this point
            check_organization_permission(
                request.user, organization_id, "view_project"  # type: ignore[arg-type]
            )

        # Let LoginRequiredMixin handle authentication check and redirect if needed
        return super().dispatch(request, *args, **kwargs)
