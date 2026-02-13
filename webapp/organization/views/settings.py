"""
Views related to organization settings.
"""

from audits.forms import AuditLibraryForm
from audits.models.audit import AuditLibrary, AuditLibraryTag
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, ListView, RedirectView, UpdateView
from organization.mixins import OrganizationPermissionMixin
from organization.models import Organization

User = get_user_model()


class SettingsIndexRedirectView(
    LoginRequiredMixin, OrganizationPermissionMixin, RedirectView
):
    """
    Redirect to the current organization's settings page.

    Uses OrganizationPermissionMixin to resolve and validate current_organization_id,
    so permissions and organization selection logic stay centralized.
    """

    model = Organization

    def get_redirect_url(self, *args, **kwargs):
        if self.current_organization_id is None:
            # Safety net – should already be enforced by the mixin.
            raise PermissionDenied("No organization selected")

        return reverse(
            "settings:organization",
            kwargs={"pk": self.current_organization_id},
        )


class OrganizationEditView(LoginRequiredMixin, OrganizationPermissionMixin, UpdateView):
    """View to edit the organization."""

    model = Organization
    fields = ["name", "description"]
    template_name = "settings/organization/edit.html"
    success_url = reverse_lazy("dashboard")

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Organization]
    ) -> QuerySet[Organization]:
        """Filter organizations by current organization."""
        if self.current_organization_id is None:
            raise PermissionDenied("No organization selected")
        return queryset.filter(id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """
        Get the organization ID from the current object.
        """
        if self.current_organization_id is None:
            raise PermissionDenied("No organization selected")
        return self.current_organization_id

    def get_success_url(self, *args, **kwargs):
        """Get the success URL."""
        return reverse(
            "settings:organization", kwargs={"pk": self.current_organization_id}
        )


class OrganizationAuditLibraryListView(
    LoginRequiredMixin, OrganizationPermissionMixin, ListView
):
    """View to list audit libraries for the current organization."""

    model = AuditLibrary
    template_name = "settings/audit_library/list.html"
    context_object_name = "audit_libraries"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[AuditLibrary]
    ) -> QuerySet[AuditLibrary]:
        """Filter audit libraries by current organization."""
        return queryset.filter(organization_id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """
        Required by OrganizationPermissionMixin.

        Not used for ListView without a single object context.
        """
        raise NotImplementedError("This view does not operate on a single object")


class OrganizationAuditLibraryEditView(
    LoginRequiredMixin, OrganizationPermissionMixin, UpdateView
):
    """View to edit an audit library for the current organization."""

    model = AuditLibrary
    form_class = AuditLibraryForm
    template_name = "settings/audit_library/edit.html"
    context_object_name = "audit_library"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[AuditLibrary]
    ) -> QuerySet[AuditLibrary]:
        """Filter audit libraries by current organization."""
        return queryset.filter(organization_id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """
        Get the organization ID from the current audit library object.
        """
        audit_library: AuditLibrary = self.get_object()  # type: ignore[assignment]
        # organization is optional on the model, but for this view, the mixin
        # already guarantees that current_organization_id is set and matches.
        return int(
            audit_library.organization_id  # type: ignore[attr-defined]
            or self.current_organization_id
            or 0
        )

    def get_form_kwargs(self) -> dict:
        """
        Inject the current organization into the form so tags are scoped correctly.
        """
        kwargs = super().get_form_kwargs()
        if self.current_organization_id is not None:
            # Lazily resolve organization through the current object or ID.
            audit_library: AuditLibrary = self.get_object()  # type: ignore[assignment]
            kwargs["organization"] = audit_library.organization
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Provide all tags available for the current organization to the template.

        All tags are loaded into the DOM so the Stimulus widget can handle tag
        assignment on the client side.
        """
        context = super().get_context_data(**kwargs)
        if self.current_organization_id is not None:
            context["all_tags"] = AuditLibraryTag.objects.filter(
                organization_id=self.current_organization_id
            ).order_by("name")
        else:
            context["all_tags"] = AuditLibraryTag.objects.none()
        return context

    def get_success_url(self, *args, **kwargs):
        """Redirect back to the edit page after saving."""
        audit_library: AuditLibrary = self.get_object()  # type: ignore[assignment]
        return reverse(
            "settings:audit_library_edit",
            kwargs={"slug": audit_library.slug},
        )


class OrganizationAuditLibraryDeleteView(
    LoginRequiredMixin, OrganizationPermissionMixin, DeleteView
):
    """View to delete an audit library for the current organization."""

    model = AuditLibrary
    template_name = "settings/audit_library/confirm_delete.html"
    context_object_name = "audit_library"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[AuditLibrary]
    ) -> QuerySet[AuditLibrary]:
        """Filter audit libraries by current organization."""
        return queryset.filter(organization_id=self.current_organization_id)

    def _get_object_organization_id(self) -> int:
        """
        Get the organization ID from the current audit library object.
        """
        audit_library: AuditLibrary = self.get_object()  # type: ignore[assignment]
        return int(audit_library.organization_id)  # type: ignore[attr-defined]

    def get_success_url(self, *args, **kwargs):
        """Redirect to the audit library list after deletion."""
        return reverse("settings:audits")


class OrganizationMemberListView(
    LoginRequiredMixin, OrganizationPermissionMixin, ListView
):
    """View to list members of the current organization."""

    model = User
    template_name = "settings/member/list.html"
    context_object_name = "members"
