from audits.models.audit import ProjectAuditCriterion
from audits.views.mixin import AuditChildrenMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.views.generic import DetailView
from organization.mixins import OrganizationPermissionMixin


class CriterionDetailView(
    LoginRequiredMixin, AuditChildrenMixin, OrganizationPermissionMixin, DetailView
):
    """Display the details of a criterion."""

    model = ProjectAuditCriterion
    template_name = "audits/projectauditcriterion/detail.html"
    context_object_name = "criterion"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[ProjectAuditCriterion]
    ) -> QuerySet[ProjectAuditCriterion]:
        return queryset.prefetch_related(
            "project_audit__project", "project_audit"
        ).filter(project_audit__project__organization_id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        if object := self.get_object():
            return object.project_audit.project.organization_id
        raise PermissionDenied("Object not found")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("criterion", "comments__user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        context["audit"] = self._get_audit()
        context["session_id"] = self.request.GET.get("session_id")
        return context
