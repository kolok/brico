from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import View
from organization.models.organization import Project


class ProjectChildrenMixin(View):
    """Mixin for views that need to access project related data."""

    def _get_project(self) -> Project:
        project_slug = self.kwargs.get("project_slug")

        # Need that class which use this mixin to have a current_organization_id
        # attribute set.
        current_organization_id = getattr(self, "current_organization_id", None)
        if current_organization_id is None:
            raise PermissionDenied("No organization selected")

        return get_object_or_404(
            Project, organization_id=current_organization_id, slug=project_slug
        )


class AuditChildrenMixin(ProjectChildrenMixin):
    """Mixin for views that need to access audit related data."""

    def _get_audit(self) -> ProjectAudit:
        audit_id = self.kwargs.get("audit_id")
        return get_object_or_404(ProjectAudit, id=audit_id)


class CriteriaChildrenMixin(AuditChildrenMixin):
    """Mixin for views that need to access criteria related data."""

    def _get_criterion(self) -> ProjectAuditCriterion:
        criterion_id = self.kwargs.get("criterion_id")
        return get_object_or_404(ProjectAuditCriterion, id=criterion_id)
