"""
Tests for organization-scoped permissions system.
"""

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from organization.permissions import (
    check_organization_permission,
    has_organization_permission,
)
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    UserFactory,
)


@pytest.fixture(scope="module")
def auth_fixture(django_db_setup, django_db_blocker):
    """Load auth fixture once per test module."""
    with django_db_blocker.unblock():
        call_command("loaddata", "content_type", verbosity=0)
        call_command("loaddata", "auth", verbosity=0)


@pytest.fixture
def admin_group(auth_fixture):
    """Load administrator group from auth fixture."""
    return Group.objects.get(name="administrator")


@pytest.fixture
def writer_group(auth_fixture):
    """Load writer group from auth fixture."""
    return Group.objects.get(name="writer")


@pytest.fixture
def reader_group(auth_fixture):
    """Load reader group from auth fixture."""
    return Group.objects.get(name="reader")


@pytest.mark.django_db
class TestHasOrganizationPermission:
    def test_administrator_has_all_permissions(self, admin_group):
        """Test that administrator has all permissions."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org, group=admin_group)

        assert has_organization_permission(user, org.id, "view_project")
        assert has_organization_permission(user, org.id, "add_project")
        assert has_organization_permission(user, org.id, "change_project")
        assert has_organization_permission(user, org.id, "delete_project")

    def test_writer_has_read_write_permissions(self, writer_group):
        """Test that writer has read and write permissions."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org, group=writer_group)

        assert has_organization_permission(user, org.id, "view_project")
        assert has_organization_permission(user, org.id, "add_project")
        assert has_organization_permission(user, org.id, "change_project")
        assert has_organization_permission(user, org.id, "delete_project")

    def test_reader_has_only_read_permissions(self, reader_group):
        """Test that reader has only read permissions."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org, group=reader_group)

        assert has_organization_permission(user, org.id, "view_project")
        assert not has_organization_permission(user, org.id, "add_project")
        assert not has_organization_permission(user, org.id, "change_project")
        assert not has_organization_permission(user, org.id, "delete_project")

    def test_non_member_has_no_permissions(self):
        """Test that non-member has no permissions."""
        user = UserFactory()
        org = OrganizationFactory()

        assert not has_organization_permission(user, org.id, "view_project")
        assert not has_organization_permission(user, org.id, "add_project")


@pytest.mark.django_db
class TestCheckOrganizationPermission:
    def test_check_permission_success(self, admin_group):
        """Test successful permission check."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org, group=admin_group)

        # Should not raise
        check_organization_permission(user, org.id, "view_project")

    def test_check_permission_failure(self, reader_group):
        """Test failed permission check raises PermissionDenied."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org, group=reader_group)

        with pytest.raises(PermissionDenied):
            check_organization_permission(user, org.id, "add_project")
