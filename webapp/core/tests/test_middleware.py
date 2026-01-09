import pytest
from core.middleware import (
    CURRENT_ORGANIZATION_SESSION_KEY,
    ORGANIZATIONS_SESSION_KEY,
    ActiveNavMiddleware,
    OrganizationMiddleware,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    UserFactory,
)

User = get_user_model()


@pytest.mark.django_db
class TestActiveNavMiddleware:
    def test_sets_projects_active_for_projects_path(self, rf):
        """Test that 'projects' is set as active for /audits/projects path."""
        middleware = ActiveNavMiddleware(lambda request: None)
        request = rf.get("/audits/project/")

        middleware(request)

        assert request.active_nav["project"] is True

    def test_sets_dashboard_active_for_dashboard_path(self, rf):
        """Test that 'dashboard' is set as active for /dashboard path."""
        middleware = ActiveNavMiddleware(lambda request: None)
        request = rf.get("/dashboard/")

        middleware(request)

        assert request.active_nav["dashboard"] is True

    def test_sets_both_active_for_nested_path(self, rf):
        """Test that both can be active for nested paths."""
        middleware = ActiveNavMiddleware(lambda request: None)
        request = rf.get("/audits/project/123/")

        middleware(request)

        assert request.active_nav["project"] is True

    def test_no_active_nav_for_other_paths(self, rf):
        """Test that no active nav is set for other paths."""
        middleware = ActiveNavMiddleware(lambda request: None)
        request = rf.get("/other/path/")

        middleware(request)

        assert "project" not in request.active_nav
        assert "dashboard" not in request.active_nav


@pytest.mark.django_db
class TestOrganizationMiddleware:
    def test_loads_user_organizations_into_session(self, rf):
        """Test that user organizations are loaded into session."""
        user = UserFactory()
        org1 = OrganizationFactory(name="Org 1")
        org2 = OrganizationFactory(name="Org 2")
        OrganizationMemberFactory(user=user, organization=org1)
        OrganizationMemberFactory(user=user, organization=org2)

        request = rf.get("/")
        request.user = user
        request.session = {}

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        assert len(request.session[ORGANIZATIONS_SESSION_KEY]) == 2
        assert (org1.id, org1.name) in request.session[ORGANIZATIONS_SESSION_KEY]
        assert (org2.id, org2.name) in request.session[ORGANIZATIONS_SESSION_KEY]

    def test_does_not_reload_organizations_if_already_in_session(self, rf):
        """Test that organizations are not reloaded if already in session."""
        user = UserFactory()
        org = OrganizationFactory(name="Org 1")
        OrganizationMemberFactory(user=user, organization=org)

        request = rf.get("/")
        request.user = user
        request.session = {
            ORGANIZATIONS_SESSION_KEY: [(999, "Existing Org")],
        }

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        # Should keep existing organizations
        assert request.session[ORGANIZATIONS_SESSION_KEY] == [(999, "Existing Org")]

    def test_sets_default_organization_when_no_current_organization(self, rf):
        """Test that default organization is set when no current organization."""
        user = UserFactory()
        org1 = OrganizationFactory(name="Org 1")
        org2 = OrganizationFactory(name="Org 2")
        OrganizationMemberFactory(user=user, organization=org1, is_default=True)
        OrganizationMemberFactory(user=user, organization=org2, is_default=False)

        request = rf.get("/")
        request.user = user
        request.session = {}

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        assert request.session[CURRENT_ORGANIZATION_SESSION_KEY] == (org1.id, org1.name)

    def test_sets_first_organization_when_no_default(self, rf):
        """Test that first organization is set when no default exists."""
        user = UserFactory()
        org1 = OrganizationFactory(name="Org 1")
        org2 = OrganizationFactory(name="Org 2")
        OrganizationMemberFactory(user=user, organization=org1, is_default=False)
        OrganizationMemberFactory(user=user, organization=org2, is_default=False)

        request = rf.get("/")
        request.user = user
        request.session = {}

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        # Should use first organization from the list
        organizations = request.session[ORGANIZATIONS_SESSION_KEY]
        assert request.session[CURRENT_ORGANIZATION_SESSION_KEY] == organizations[0]

    def test_does_not_set_current_organization_if_already_set(self, rf):
        """Test that current organization is not changed if already set."""
        user = UserFactory()
        org1 = OrganizationFactory(name="Org 1")
        org2 = OrganizationFactory(name="Org 2")
        OrganizationMemberFactory(user=user, organization=org1, is_default=True)
        OrganizationMemberFactory(user=user, organization=org2, is_default=False)

        request = rf.get("/")
        request.user = user
        request.session = {
            CURRENT_ORGANIZATION_SESSION_KEY: (999, "Existing Org"),
        }

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        # Should keep existing current organization
        assert request.session[CURRENT_ORGANIZATION_SESSION_KEY] == (
            999,
            "Existing Org",
        )

    def test_does_not_process_for_unauthenticated_user(self, rf):
        """Test that middleware does not process for unauthenticated users."""

        request = rf.get("/")
        request.user = AnonymousUser()
        request.session = {}

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        assert ORGANIZATIONS_SESSION_KEY not in request.session
        assert CURRENT_ORGANIZATION_SESSION_KEY not in request.session

    def test_handles_user_with_no_organizations(self, rf):
        """Test that middleware handles users with no organizations."""
        user = UserFactory()

        request = rf.get("/")
        request.user = user
        request.session = {}

        middleware = OrganizationMiddleware(lambda request: None)
        middleware(request)

        assert request.session[ORGANIZATIONS_SESSION_KEY] == []
        assert CURRENT_ORGANIZATION_SESSION_KEY not in request.session
