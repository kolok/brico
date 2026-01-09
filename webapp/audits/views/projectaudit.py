from audits.forms import NewAuditForm
from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from audits.views.mixin import ProjectChildrenMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView
from organization.mixins import OrganizationPermissionMixin


class ProjectAuditViewMixin(OrganizationPermissionMixin, ProjectChildrenMixin):
    """Mixin to filter and check permissions by organization."""

    model = ProjectAudit

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[ProjectAudit]
    ) -> QuerySet[ProjectAudit]:
        return queryset.prefetch_related("project").filter(
            project__organization_id=self.current_organization_id
        )

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        if object := self.get_object():
            return object.project.organization_id
        raise PermissionDenied("Object not found")


class ProjectAuditDetailView(LoginRequiredMixin, ProjectAuditViewMixin, DetailView):
    """Display audit details."""

    template_name = "audits/projectaudit/detail.html"
    context_object_name = "audit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        return context

    def get_queryset(self):
        project = self._get_project()
        queryset = super().get_queryset()
        queryset = queryset.filter(project=project)
        return queryset.prefetch_related(
            "project_audit_criteria", "project_audit_criteria__criterion"
        )


class NewProjectAuditView(LoginRequiredMixin, ProjectAuditViewMixin, FormView):
    """Create a new audit for a project."""

    form_class = NewAuditForm
    template_name = "audits/projectaudit/new.html"
    model = ProjectAudit

    def get_success_url(self):
        return reverse_lazy(
            "audits:project_detail", kwargs={"slug": self._get_project().slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        return context

    def form_valid(self, form):
        audit_library = form.cleaned_data.get("audit_library")
        project_audit = ProjectAudit.objects.create(
            project=self._get_project(),
            audit_library=audit_library,
        )
        for criterion in audit_library.criterias.all():
            ProjectAuditCriterion.objects.create(
                project_audit=project_audit,
                criterion=criterion,
            )
        messages.success(self.request, _("Audit created successfully"))
        return super().form_valid(form)


# FIXME : use DeleteView
class DeleteProjectAuditView(LoginRequiredMixin, ProjectAuditViewMixin, DeleteView):
    model = ProjectAudit
    template_name = "audits/projectaudit/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "audits:project_detail", kwargs={"slug": self._get_project().slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        return context
