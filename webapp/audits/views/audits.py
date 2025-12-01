from audits.forms import NewAuditForm
from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from audits.views.mixin import ProjectChildrenMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from organization.models.organization import Project


class AuditDetailView(LoginRequiredMixin, ProjectChildrenMixin, DetailView):
    """Display audit details."""

    model = ProjectAudit
    template_name = "audits/audit_detail.html"
    context_object_name = "audit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            "project_audit_criteria", "project_audit_criteria__criterion"
        )


class NewAuditView(LoginRequiredMixin, FormView):
    """Create a new audit for a project."""

    form_class = NewAuditForm
    template_name = "audits/new_audit.html"
    success_url = reverse_lazy("audits:project_detail")

    def get_success_url(self):
        return reverse_lazy(
            "audits:project_detail", kwargs={"slug": self._get_project().slug}
        )

    def _get_project(self) -> Project:
        return get_object_or_404(Project, slug=self.kwargs.get("project_slug"))

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


@login_required
def delete_audit(request, project_slug, pk):
    audit = get_object_or_404(ProjectAudit, id=pk)
    audit.delete()
    messages.success(request, _("Audit deleted successfully"))
    return redirect("audits:project_detail", slug=project_slug)
