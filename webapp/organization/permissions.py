"""
Permission mixins and utilities for organization-scoped access control.

These mixins check:
1. User is authenticated
2. Resource belongs to current organization
3. User has required role/permissions in that organization
"""

from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from organization.models import OrganizationMember


class OrganizationPermissionMixin(LoginRequiredMixin):
    """
    Base mixin for organization-scoped permission checks.
    
    Verifies that:
    - User belongs to the current organization
    - Resource (if applicable) belongs to current organization
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Check organization membership before dispatching."""
        # Let LoginRequiredMixin handle authentication
        response = super().dispatch(request, *args, **kwargs)
        
        # Get current organization from session
        current_org = request.session.get(CURRENT_ORGANIZATION_SESSION_KEY)
        if not current_org:
            raise PermissionDenied("No organization selected")
        
        organization_id = current_org[0]
        
        # Verify user belongs to this organization
        try:
            self.organization_member = OrganizationMember.objects.select_related(
                'role', 'organization'
            ).get(
                user=request.user,
                organization_id=organization_id
            )
        except OrganizationMember.DoesNotExist:
            raise PermissionDenied("You do not belong to this organization")
        
        return response
    
    def get_queryset(self):
        """Filter queryset to current organization."""
        queryset = super().get_queryset()
        current_org = self.request.session.get(CURRENT_ORGANIZATION_SESSION_KEY)
        if current_org:
            organization_id = current_org[0]
            # Assuming the model has an 'organization' field
            if hasattr(queryset.model, 'organization'):
                queryset = queryset.filter(organization_id=organization_id)
            # For models like Resource that have project__organization
            elif hasattr(queryset.model, 'project'):
                queryset = queryset.filter(project__organization_id=organization_id)
        return queryset


class OrganizationAdminRequiredMixin(OrganizationPermissionMixin):
    """Requires administrator role in the current organization."""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if self.organization_member.role.name != 'administrator':
            raise PermissionDenied("Administrator role required")
        
        return response


class OrganizationWritePermissionMixin(OrganizationPermissionMixin):
    """Requires writer or administrator role in the current organization."""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if self.organization_member.role.name not in ['administrator', 'writer']:
            raise PermissionDenied("Writer or administrator role required")
        
        return response


class OrganizationReadPermissionMixin(OrganizationPermissionMixin):
    """
    Requires any role (reader, writer, or administrator) in the current organization.
    This is effectively just the OrganizationPermissionMixin.
    """
    pass


def check_organization_permission(user, organization_id, required_role=None, required_permission=None):
    """
    Utility function to check if a user has permission in an organization.
    
    Args:
        user: The user to check
        organization_id: The organization ID
        required_role: One of 'reader', 'writer', 'administrator' (optional)
        required_permission: Django permission codename (optional)
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    try:
        member = OrganizationMember.objects.select_related('role').get(
            user=user,
            organization_id=organization_id
        )
        
        # Check role if specified
        if required_role:
            role_hierarchy = {
                'reader': ['reader', 'writer', 'administrator'],
                'writer': ['writer', 'administrator'],
                'administrator': ['administrator']
            }
            if member.role.name not in role_hierarchy.get(required_role, []):
                return False
        
        # Check specific permission if specified
        if required_permission:
            return member.has_permission(required_permission)
        
        return True
        
    except OrganizationMember.DoesNotExist:
        return False


def get_user_role_in_organization(user, organization_id):
    """
    Get the user's role in a specific organization.
    
    Returns:
        Role object or None if user is not a member
    """
    try:
        member = OrganizationMember.objects.select_related('role').get(
            user=user,
            organization_id=organization_id
        )
        return member.role
    except OrganizationMember.DoesNotExist:
        return None
