from audits.models.audit import ProjectAuditCriterion
from audits.views.mixin import AuditChildrenMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView


class CriterionDetailView(LoginRequiredMixin, AuditChildrenMixin, DetailView):
    """Display the details of a criterion."""

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
