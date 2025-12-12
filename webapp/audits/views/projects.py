from audits.forms import ProjectForm
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from organization.models.organization import Organization, OrganizationMember, Project
from organization.permissions import (
    OrganizationReadPermissionMixin,
    OrganizationWritePermissionMixin,
)


class ProjectListView(OrganizationReadPermissionMixin, ListView):
    """List all user projects - requires read permission in current organization."""

    model = Project
    template_name = "audits/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        # OrganizationReadPermissionMixin already filters by organization
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset


class ProjectDetailView(OrganizationReadPermissionMixin, DetailView):
    """Display project details - requires read permission in current organization."""

    model = Project
    template_name = "audits/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            "resources", "audits", "audits__project_audit_criteria"
        )


class ProjectFormView(OrganizationWritePermissionMixin, FormView):
    """Create a new project - requires write permission in current organization."""

    form_class = ProjectForm
    template_name = "audits/new_project.html"
    slug: str | None = None

    def get_success_url(self):
        return reverse_lazy("audits:project_detail", kwargs={"slug": self.slug})

    def form_valid(self, form: ProjectForm) -> HttpResponse:
        project = form.save(commit=False)
        
        # Organization membership is already verified by OrganizationWritePermissionMixin
        # Just assign the organization from the member
        project.organization = self.organization_member.organization
        project.save()
        self.slug = project.slug
        return super().form_valid(form)
