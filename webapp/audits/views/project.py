from audits.forms import ProjectForm, SearchForm
from audits.models.audit import ProjectAudit
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from organization.mixins import OrganizationPermissionMixin
from organization.models.organization import Organization, Project


class ProjectViewMixin(OrganizationPermissionMixin):
    """Mixin to filter and check permissions by organization."""

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Project]
    ) -> QuerySet[Project]:
        return queryset.filter(organization_id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        if object := self.get_object():
            return object.organization_id
        raise PermissionDenied("Object not found")


class ProjectListView(LoginRequiredMixin, ProjectViewMixin, ListView):
    """List all user projects."""

    model = Project
    template_name = "audits/project/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET or None)
        # Prefetch active and archived audits separately using to_attr
        active_audits = Prefetch(
            "audits",
            queryset=ProjectAudit.objects.get_active()
            .select_related("audit_library")
            .prefetch_related(
                "project_audit_criteria",
                "project_audit_criteria__criterion",
            ),
            to_attr="active_audits_list",
        )
        archived_audits = Prefetch(
            "audits",
            queryset=ProjectAudit.objects.get_archived(),
            to_attr="archived_audits_list",
        )
        queryset = queryset.prefetch_related(active_audits, archived_audits)
        search_query = ""
        if form.is_valid():
            search_query = form.cleaned_data.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(self.request.GET or None)
        return context


class ProjectDetailView(LoginRequiredMixin, ProjectViewMixin, DetailView):
    """Display project details."""

    model = Project
    template_name = "audits/project/detail.html"
    context_object_name = "project"


class ProjectFormView(LoginRequiredMixin, ProjectViewMixin, FormView):
    """Create a new project."""

    form_class = ProjectForm
    template_name = "audits/project/new.html"
    model = Project
    slug: str | None = None

    def get_success_url(self):
        return reverse_lazy("audits:project_detail", kwargs={"slug": self.slug})

    def form_valid(self, form: ProjectForm) -> HttpResponse:
        project = form.save(commit=False)
        organization_id = self.request.session.get(
            CURRENT_ORGANIZATION_SESSION_KEY, [None]
        )[0]
        organization = Organization.objects.filter(id=organization_id).first()
        if organization is None:
            raise PermissionDenied(
                "No organization is configured. Please contact an administrator."
            )

        project.organization = organization
        project.save()
        self.slug = project.slug
        return super().form_valid(form)


class DeleteProjectView(LoginRequiredMixin, ProjectViewMixin, DeleteView):
    """Delete a project."""

    model = Project
    template_name = "audits/project/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("audits:project_list")
