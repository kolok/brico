from audits.forms import CommentForm
from audits.models.audit import (
    ProjectAudit,
    ProjectAuditCriterion,
    ProjectAuditCriterionComment,
)
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from organization.models.organization import Project


class CommentParentMixin(View):
    def _get_project(self):
        return get_object_or_404(Project, slug=self.kwargs.get("project_slug"))

    def _get_audit(self):
        return get_object_or_404(ProjectAudit, id=self.kwargs.get("audit_id"))

    def _get_criterion(self):
        criterion_id = self.kwargs.get("criterion_id")
        return get_object_or_404(ProjectAuditCriterion, id=criterion_id)


# Comment views
class CommentListView(LoginRequiredMixin, CommentParentMixin, TemplateView):
    """Affiche la liste des commentaires d'un critère."""

    template_name = "audits/comments_list.html"

    def get_queryset(self):
        # TODO: this one is perhaps useless
        queryset = super().get_queryset()
        return queryset.prefetch_related("criterion__project_audit__project")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        criterion_id = self.kwargs.get("criterion_id")
        criterion = get_object_or_404(ProjectAuditCriterion, id=criterion_id)
        context["criterion"] = criterion
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        context["comments"] = (
            criterion.comments.all().select_related("user").order_by("-created_at")
        )
        return context


class CommentCreateView(LoginRequiredMixin, CommentParentMixin, CreateView):
    """Crée un nouveau commentaire."""

    model = ProjectAuditCriterionComment
    form_class = CommentForm
    template_name = "audits/comment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        context["audit"] = self._get_audit()
        context["criterion"] = self._get_criterion()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.project_audit_criterion = self._get_criterion()
        messages.success(self.request, _("Comment created successfully"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "criterion_id": self._get_criterion().id,
            },
        )


class CommentUpdateView(LoginRequiredMixin, CommentParentMixin, UpdateView):
    """Modifie un commentaire existant."""

    model = ProjectAuditCriterionComment
    form_class = CommentForm
    template_name = "audits/comment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["criterion"] = self._get_criterion()
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Comment updated successfully"))
        response = super().form_valid(form)
        obj = getattr(self, "object", None)

        if obj and self.request.headers.get("Turbo-Frame"):
            return redirect(
                "audits:comment_fragment",
                project_slug=self._get_project().slug,
                audit_id=self._get_audit().id,
                criterion_id=self._get_criterion().id,
                pk=obj.id,
            )

        return response

    def get_success_url(self):
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "criterion_id": self._get_criterion().id,
            },
        )


class CommentDeleteView(LoginRequiredMixin, CommentParentMixin, DeleteView):
    """Supprime un commentaire."""

    model = ProjectAuditCriterionComment
    template_name = "audits/comment_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["criterion"] = self._get_criterion()
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": self._get_project().slug,
                "audit_id": self._get_audit().id,
                "criterion_id": self._get_criterion().id,
            },
        )


class CommentFormCancelView(LoginRequiredMixin, TemplateView):
    """Vide le formulaire de commentaire."""

    template_name = "audits/comment_form_empty.html"


class CommentFragmentView(LoginRequiredMixin, CommentParentMixin, TemplateView):
    """Réaffiche un commentaire dans son Turbo Frame."""

    template_name = "audits/comment_item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        context["audit"] = self._get_audit()
        context["criterion"] = self._get_criterion()
        context["comment"] = get_object_or_404(
            ProjectAuditCriterionComment,
            id=self.kwargs.get("pk"),
            project_audit_criterion=self._get_criterion(),
        )
        return context
