from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from organization.models.organization import Project


class ProjectListView(LoginRequiredMixin, ListView):
    """List all user projects."""

    model = Project
    template_name = "audits/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.all()


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
