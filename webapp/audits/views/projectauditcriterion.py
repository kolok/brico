from audits.forms import StatusUpdateForm
from audits.models.audit import ProjectAuditCriterion
from audits.views.mixin import AuditChildrenMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from organization.mixins import OrganizationPermissionMixin


class CriterionDetailView(
    LoginRequiredMixin, OrganizationPermissionMixin, AuditChildrenMixin, UpdateView
):
    """Display and update the details of a criterion."""

    context_object_name = "criterion"
    form_class = StatusUpdateForm
    model = ProjectAuditCriterion
    template_name = "audits/projectauditcriterion/detail.html"

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
            assert isinstance(object, ProjectAuditCriterion)
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

    def get_success_url(self):
        return reverse_lazy(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "pk": self.get_object().id,
            },
        )
