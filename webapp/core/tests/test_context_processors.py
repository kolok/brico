import pytest
from core.context_processors import organization_context
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY, ORGANIZATIONS_SESSION_KEY


@pytest.mark.django_db
class TestOrganizationContext:
    def test_returns_user_organizations_from_session(self, rf):
        """Test that user organizations are returned from session."""
        request = rf.get("/")
        request.session = {
            ORGANIZATIONS_SESSION_KEY: [(1, "Org 1"), (2, "Org 2")],
        }

        context = organization_context(request)

        assert context["user_organizations"] == [(1, "Org 1"), (2, "Org 2")]

    def test_returns_empty_list_when_no_organizations_in_session(self, rf):
        """Test that empty list is returned when no organizations in session."""
        request = rf.get("/")
        request.session = {}

        context = organization_context(request)

        assert context["user_organizations"] == []

    def test_returns_current_organization_from_session(self, rf):
        """Test that current organization is returned from session."""
        request = rf.get("/")
        request.session = {
            CURRENT_ORGANIZATION_SESSION_KEY: (1, "Current Org"),
        }

        context = organization_context(request)

        assert context["current_organization"] == (1, "Current Org")

    def test_returns_none_when_no_current_organization_in_session(self, rf):
        """Test that None is returned when no current organization in session."""
        request = rf.get("/")
        request.session = {}

        context = organization_context(request)

        assert context["current_organization"] is None

    def test_returns_both_organizations_and_current(self, rf):
        """Test that both user organizations and current organization are returned."""
        request = rf.get("/")
        request.session = {
            ORGANIZATIONS_SESSION_KEY: [(1, "Org 1"), (2, "Org 2")],
            CURRENT_ORGANIZATION_SESSION_KEY: (1, "Org 1"),
        }

        context = organization_context(request)

        assert context["user_organizations"] == [(1, "Org 1"), (2, "Org 2")]
        assert context["current_organization"] == (1, "Org 1")
