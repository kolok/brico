"""
Mixins for views that need organization-scoped permission checks.
"""

from abc import abstractmethod

from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.views.generic import DeleteView
from organization.permissions import check_organization_permission


class OrganizationPermissionMixin:
    """
    Mixin to check organization permissions for views.

    Requires the view to have a model attribute and get_object() method.
    """

    current_organization_id: int | None = None

    @abstractmethod
    def _get_queryset_with_organization_filter(self, queryset: QuerySet) -> QuerySet:
        """
        Get queryset with organization filter,
        to be implemented by the View which implement this mixin.
        """

    @abstractmethod
    def _get_object_organization_id(self) -> int:
        """
        Get the organization ID, to be implemented by the View which implement this
        mixin.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def _get_permission_codename(self, method: str | None) -> str:
        """
        Map HTTP method to permission codename.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)

        Returns:
            Permission codename
        """
        model_name = self.model._meta.model_name

        # DeleteView use case : Django DeleteView use POST method to delete an object
        if isinstance(self, DeleteView):
            return f"delete_{model_name}"

        # Other cases
        if method == "GET":
            return f"view_{model_name}"
        elif method in ("POST", "PUT", "PATCH"):
            # Check if it's create or update
            try:
                if hasattr(self, "get_object") and self.get_object():
                    return f"change_{model_name}"
                return f"add_{model_name}"
            except AttributeError:
                return f"add_{model_name}"
        elif method == "DELETE":
            return f"delete_{model_name}"
        else:
            return f"view_{model_name}"

    def dispatch(self, request, *args, **kwargs):
        """Check object permissions before dispatching."""

        self.current_organization_id = request.session.get(
            CURRENT_ORGANIZATION_SESSION_KEY, [None]
        )[0]
        if self.current_organization_id is None:
            raise PermissionDenied("No organization selected")

        if hasattr(self, "get_object"):
            try:
                object = self.get_object()
                if object is not None:
                    # Get the organization ID from the object
                    # And check the object belongs to the current organization
                    object_organization_id = self._get_object_organization_id()
                    if object_organization_id != self.current_organization_id:
                        raise PermissionDenied(
                            "Object does not belong to current organization"
                        )
            except AttributeError:
                pass  # ListView, FormView without object
        permission_codename = self._get_permission_codename(request.method)
        check_organization_permission(
            request.user, self.current_organization_id, permission_codename
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self._get_queryset_with_organization_filter(queryset)
        return queryset
