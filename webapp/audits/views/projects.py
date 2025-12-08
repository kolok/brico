from audits.forms import ProjectForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from organization.models.organization import Organization, Project


class ProjectListView(LoginRequiredMixin, ListView):
    """List all user projects."""

    model = Project
    template_name = "audits/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.all().prefetch_related("resources", "audits")
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

    def form_valid(self, form):
        project = form.save(commit=False)
        # TODO: get the organization from the session
        project.organization = Organization.objects.all().first()
        project.save()
        self.slug = project.slug
        return super().form_valid(form)
