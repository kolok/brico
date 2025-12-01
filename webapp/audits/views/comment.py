from audits.forms import CommentForm
from audits.models.audit import ProjectAuditCriterion, ProjectAuditCriterionComment
from audits.views.mixin import CriteriaChildrenMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView


class CommentListView(LoginRequiredMixin, CriteriaChildrenMixin, TemplateView):
    """Display the list of comments for a criterion."""

    template_name = "audits/comments_list.html"

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


class CommentCreateView(LoginRequiredMixin, CriteriaChildrenMixin, CreateView):
    """Create a new comment."""

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


class CommentUpdateView(LoginRequiredMixin, CriteriaChildrenMixin, UpdateView):
    """Update an existing comment."""

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


class CommentDeleteView(LoginRequiredMixin, CriteriaChildrenMixin, DeleteView):
    """Delete a comment."""

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
    """Empty the comment form."""

    template_name = "audits/comment_form_empty.html"


class CommentFragmentView(LoginRequiredMixin, CriteriaChildrenMixin, TemplateView):
    """Re-display a comment in its Turbo Frame."""

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
