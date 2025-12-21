from audits.forms import CommentForm
from audits.models.audit import Comment, ProjectAuditCriterion
from audits.views.mixin import CriteriaChildrenMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from organization.mixins import OrganizationPermissionMixin


class CommentPermissionMixin(OrganizationPermissionMixin):
    """Mixin to check comment permissions."""

    model = Comment

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Comment]
    ) -> QuerySet[Comment]:
        return queryset.prefetch_related(
            "project_audit_criterion__project_audit__project"
        ).filter(
            project_audit_criterion__project_audit__project__organization_id=(
                self.current_organization_id
            )
        )

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        obj = self.get_object()  # type: ignore[misc]
        if obj:
            project = obj.project_audit_criterion.project_audit.project
            return project.organization_id
        raise PermissionDenied("Object not found")

    def _get_criterion_filtered(self) -> ProjectAuditCriterion:
        """Get criterion filtered by organization."""
        criterion_id = self.kwargs.get("criterion_id")  # type: ignore[attr-defined]
        return get_object_or_404(
            ProjectAuditCriterion.objects.prefetch_related(
                "project_audit__project"
            ).filter(
                project_audit__project__organization_id=self.current_organization_id
            ),
            id=criterion_id,
        )


class CommentListView(
    LoginRequiredMixin, CriteriaChildrenMixin, CommentPermissionMixin, TemplateView
):
    """Display the list of comments for a criterion."""

    template_name = "audits/comment/list.html"

    def get_object(self):
        """Get the criterion filtered by organization."""
        return self._get_criterion_filtered()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        criterion = self.get_object()
        context["criterion"] = criterion
        context["audit"] = self._get_audit()
        context["project"] = self._get_project()
        # Filter comments by organization using the mixin's filter method
        comments_queryset = Comment.objects.filter(
            project_audit_criterion=criterion
        ).select_related("user")
        context["comments"] = self._get_queryset_with_organization_filter(
            comments_queryset
        ).order_by("-created_at")
        return context


class CommentCreateView(
    LoginRequiredMixin, CriteriaChildrenMixin, CommentPermissionMixin, CreateView
):
    """Create a new comment."""

    model = Comment
    form_class = CommentForm
    template_name = "audits/comment/form.html"

    def get_object(self):
        """Return None for CreateView, but ensure criterion is filtered."""
        # This method is called by the mixin's dispatch to check permissions
        # For CreateView, we need to verify the criterion belongs to the organization
        self._get_criterion_filtered()
        return None  # CreateView doesn't have an object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        criterion = self._get_criterion_filtered()
        context["project"] = criterion.project_audit.project
        context["audit"] = criterion.project_audit
        context["criterion"] = criterion
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.project_audit_criterion = self._get_criterion_filtered()
        messages.success(self.request, _("Comment created successfully"))
        return super().form_valid(form)

    def get_success_url(self):
        criterion = self._get_criterion_filtered()
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": criterion.project_audit.project.slug,
                "audit_id": criterion.project_audit.id,
                "criterion_id": criterion.id,
            },
        )


class CommentUpdateView(
    LoginRequiredMixin, CriteriaChildrenMixin, CommentPermissionMixin, UpdateView
):
    """Update an existing comment."""

    model = Comment
    form_class = CommentForm
    template_name = "audits/comment/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get_object() already filters by organization via get_queryset()
        comment = self.get_object()
        assert isinstance(comment, Comment)
        criterion = comment.project_audit_criterion
        context["criterion"] = criterion
        context["audit"] = criterion.project_audit
        context["project"] = criterion.project_audit.project
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Comment updated successfully"))
        response = super().form_valid(form)
        obj = getattr(self, "object", None)

        if obj and self.request.headers.get("Turbo-Frame"):
            assert isinstance(obj, Comment)
            criterion = obj.project_audit_criterion
            return redirect(
                "audits:comment_fragment",
                project_slug=criterion.project_audit.project.slug,
                audit_id=criterion.project_audit.id,
                criterion_id=criterion.id,
                pk=obj.id,
            )

        return response

    def get_success_url(self):
        comment = self.get_object()
        assert isinstance(comment, Comment)
        criterion = comment.project_audit_criterion
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": criterion.project_audit.project.slug,
                "audit_id": criterion.project_audit.id,
                "criterion_id": criterion.id,
            },
        )


class CommentDeleteView(
    LoginRequiredMixin, CriteriaChildrenMixin, CommentPermissionMixin, DeleteView
):
    """Delete a comment."""

    model = Comment
    template_name = "audits/comment/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get_object() already filters by organization via get_queryset()
        comment = self.get_object()
        assert isinstance(comment, Comment)
        criterion = comment.project_audit_criterion
        context["criterion"] = criterion
        context["audit"] = criterion.project_audit
        context["project"] = criterion.project_audit.project
        return context

    def get_success_url(self):
        comment = self.get_object()
        assert isinstance(comment, Comment)
        criterion = comment.project_audit_criterion
        return reverse_lazy(
            "audits:comments_list",
            kwargs={
                "project_slug": criterion.project_audit.project.slug,
                "audit_id": criterion.project_audit.id,
                "criterion_id": criterion.id,
            },
        )


class CommentFormCancelView(LoginRequiredMixin, CommentPermissionMixin, TemplateView):
    """Empty the comment form."""

    template_name = "audits/comment/form_empty.html"


class CommentFragmentView(
    LoginRequiredMixin, CriteriaChildrenMixin, CommentPermissionMixin, TemplateView
):
    """Re-display a comment in its Turbo Frame."""

    template_name = "audits/comment/item.html"

    def get_object(self):
        """Get the comment filtered by organization."""
        comment_id = self.kwargs.get("pk")
        # Filter criterion by organization first
        criterion = self._get_criterion_filtered()
        # Filter comment by organization
        queryset = Comment.objects.filter(
            id=comment_id, project_audit_criterion=criterion
        )
        return get_object_or_404(self._get_queryset_with_organization_filter(queryset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        assert isinstance(comment, Comment)
        criterion = comment.project_audit_criterion
        context["project"] = criterion.project_audit.project
        context["audit"] = criterion.project_audit
        context["criterion"] = criterion
        context["comment"] = comment
        return context
