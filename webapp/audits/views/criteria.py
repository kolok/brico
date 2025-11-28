from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from organization.models.organization import Project


class CriterionDetailView(LoginRequiredMixin, DetailView):
    """Affiche les détails d'une critère."""

    model = ProjectAuditCriterion
    template_name = "audits/criterion_detail.html"
    context_object_name = "criterion"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("criterion", "comments__user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        context["audit"] = self._get_audit()
        context["session_id"] = self.request.GET.get("session_id")
        return context

    def _get_project(self):
        return get_object_or_404(Project, slug=self.kwargs.get("project_slug"))

    def _get_audit(self):
        return get_object_or_404(ProjectAudit, id=self.kwargs.get("audit_id"))
