from audits.forms import ProjectForm
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from organization.models.organization import Organization, Project


class ProjectListView(LoginRequiredMixin, ListView):
    """List all user projects."""

    model = Project
    template_name = "audits/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        organization_id = self.request.session.get(
            CURRENT_ORGANIZATION_SESSION_KEY, [None]
        )[0]
        queryset = Project.objects.filter(organization=organization_id)
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Display project details."""

    model = Project
    template_name = "audits/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            "resources", "audits", "audits__project_audit_criteria"
        )


class ProjectFormView(LoginRequiredMixin, FormView):
    """Create a new project."""

    form_class = ProjectForm
    template_name = "audits/new_project.html"
    slug: str | None = None

    def get_success_url(self):
        return reverse_lazy("audits:project_detail", kwargs={"slug": self.slug})

    def form_valid(self, form: ProjectForm) -> HttpResponse:
        project = form.save(commit=False)
        # TODO: get the organization from the session
        organization_id = self.request.session.get(
            CURRENT_ORGANIZATION_SESSION_KEY, [None]
        )[0]
        organization = Organization.objects.filter(id=organization_id).first()
        if organization is None:
            form.add_error(
                None,
                _("No organization is configured. Please contact an administrator."),
            )
            return self.form_invalid(form)

        project.organization = organization
        project.save()
        self.slug = project.slug
        return super().form_valid(form)
