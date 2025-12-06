"""
Views for core application.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class IndexView(TemplateView):
    """View for the home page. Redirects authenticated users to dashboard."""

    template_name = "index.html"

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """View for the dashboard page (authenticated users only)."""

    template_name = "dashboard.html"
