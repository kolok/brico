from audits.forms import ResourceForm
from audits.views.mixin import ProjectChildrenMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from organization.mixins import OrganizationPermissionMixin
from organization.models.organization import Resource


class ResourceViewMixin(OrganizationPermissionMixin, ProjectChildrenMixin):
    """
    Mixin to filter and check permissions by organization.
    Mixin is also used to factorize common behavior of all Resource views.
    """

    model = Resource
    context_object_name = "resource"

    def _get_queryset_with_organization_filter(
        self, queryset: QuerySet[Resource]
    ) -> QuerySet[Resource]:
        return queryset.prefetch_related("project").filter(
            project__organization_id=self.current_organization_id
        )

    def _get_object_organization_id(self) -> int:
        """Get object organization ID."""
        if not hasattr(self, "get_object"):
            raise PermissionDenied("Object not found")
        if object := self.get_object():
            assert isinstance(object, Resource)
            return object.project.organization_id
        raise PermissionDenied("Object not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self._get_project()
        return context

    def get_queryset(self):
        project = self._get_project()
        queryset = super().get_queryset()
        queryset = queryset.filter(project=project)
        return queryset

    def get_success_url(self):
        return reverse_lazy(
            "audits:project_detail", kwargs={"slug": self._get_project().slug}
        )


class ResourceDetailView(LoginRequiredMixin, ResourceViewMixin, DetailView):
    """Display resource details."""

    template_name = "audits/resource/detail.html"


class NewResourceView(LoginRequiredMixin, ResourceViewMixin, CreateView):
    """Create a new resource for a project."""

    form_class = ResourceForm
    template_name = "audits/resource/new.html"

    def form_valid(self, form):
        form.instance.project = self._get_project()
        messages.success(self.request, _("Resource created successfully"))
        return super().form_valid(form)


class EditResourceView(LoginRequiredMixin, ResourceViewMixin, UpdateView):
    """Edit an existing resource."""

    form_class = ResourceForm
    template_name = "audits/resource/edit.html"

    def form_valid(self, form):
        messages.success(self.request, _("Resource updated successfully"))
        return super().form_valid(form)


class DeleteResourceView(LoginRequiredMixin, ResourceViewMixin, DeleteView):
    """Delete a resource."""

    template_name = "audits/resource/confirm_delete.html"
