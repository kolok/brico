"""
Custom permissions system for organization-scoped resources.

This module provides permission checks that verify:
1. The resource belongs to the current organization
2. The user has the appropriate role (administrator, writer, reader)
   in that organization
"""

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from organization.models.organization import OrganizationMember


def has_organization_permission(
    user: "User", organization_id: int, permission_codename: str
) -> bool:
    """
    Check if a user has a specific permission in an organization.

    Args:
        user: The user to check
        organization_id: The organization ID
        permission_codename: The permission codename (e.g., 'view_project')

    Returns:
        True if the user has the permission, False otherwise
    """

    try:
        membership = OrganizationMember.objects.select_related("group").get(
            user=user, organization_id=organization_id
        )
        if membership.group:
            return membership.group.permissions.filter(
                codename=permission_codename
            ).exists()
    except OrganizationMember.DoesNotExist:
        pass

    return False


def check_organization_permission(
    user: "User",
    organization_id: int,
    permission_codename: str,
) -> None:
    """
    Check if a user has a specific permission in an organization,
    raise PermissionDenied if not.

    Args:
        user: The user to check
        organization_id: The organization ID
        permission_codename: The permission codename

    Raises:
        PermissionDenied: If the user doesn't have the permission
    """
    if not has_organization_permission(user, organization_id, permission_codename):
        raise PermissionDenied(
            f"User {user.username} does not have permission '{permission_codename}' "
            f"in organization {organization_id}"
        )
