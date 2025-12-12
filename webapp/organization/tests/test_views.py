import pytest
from core.middleware import ORGANIZATION_ID_SESSION_KEY
from django.contrib.messages import get_messages
from django.urls import reverse
from organization.models import Organization, OrganizationMember
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestOrganizationCreateView:
    def test_redirects_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get(reverse("organization:create"))

        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_shows_create_form_when_authenticated(self, client):
        """Test that authenticated users can see the create form."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(reverse("organization:create"))

        assert response.status_code == 200

    def test_creates_organization_and_membership(self, client):
        """Test that creating an organization also creates a membership."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.post(
            reverse("organization:create"),
            {"name": "New Organization", "description": "Test description"},
        )

        assert response.status_code == 302
        assert response.url == reverse("dashboard")

        # Check organization was created
        org = Organization.objects.get(name="New Organization")
        assert org.description == "Test description"

        # Check membership was created
        membership = OrganizationMember.objects.get(user=user, organization=org)
        assert membership.is_default is True

    def test_sets_first_organization_as_default(self, client):
        """Test that the first organization is set as default."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.post(
            reverse("organization:create"),
            {"name": "First Organization", "description": ""},
        )

        assert response.status_code == 302

        membership = OrganizationMember.objects.get(
            user=user, organization__name="First Organization"
        )
        assert membership.is_default is True

    def test_sets_subsequent_organizations_as_non_default(self, client):
        """Test that subsequent organizations are not set as default."""
        user = UserFactory()
        org1 = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org1, is_default=True)
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.post(
            reverse("organization:create"),
            {"name": "Second Organization", "description": ""},
        )

        assert response.status_code == 302

        membership = OrganizationMember.objects.get(
            user=user, organization__name="Second Organization"
        )
        assert membership.is_default is False

    def test_sets_organization_as_current_in_session(self, client):
        """Test that created organization is set as current in session."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.post(
            reverse("organization:create"),
            {"name": "New Organization", "description": ""},
        )

        assert response.status_code == 302

        org = Organization.objects.get(name="New Organization")
        session = client.session
        # Django serializes tuples as lists in sessions
        session_value = session[ORGANIZATION_ID_SESSION_KEY]
        assert session_value == [org.id, org.name] or session_value == (
            org.id,
            org.name,
        )

    def test_form_validation_errors(self, client):
        """Test that form validation errors are shown."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.post(
            reverse("organization:create"),
            {"name": "", "description": ""},  # Empty name should fail
        )

        assert response.status_code == 200
        assert "form" in response.context or "error" in str(response.content).lower()


@pytest.mark.django_db
class TestOrganizationSwitchView:
    def test_redirects_to_login_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected to login."""
        org = OrganizationFactory()
        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": org.id})
        )

        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_switches_to_valid_organization(self, client):
        """Test that user can switch to an organization they belong to."""
        user = UserFactory()
        org1 = OrganizationFactory(name="Org 1")
        org2 = OrganizationFactory(name="Org 2")
        OrganizationMemberFactory(user=user, organization=org1)
        OrganizationMemberFactory(user=user, organization=org2)
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": org2.id})
        )

        assert response.status_code == 302
        assert response.url == reverse("dashboard")

        session = client.session
        # Django serializes tuples as lists in sessions
        session_value = session[ORGANIZATION_ID_SESSION_KEY]
        assert session_value == [org2.id, org2.name] or session_value == (
            org2.id,
            org2.name,
        )

    def test_shows_success_message_on_switch(self, client):
        """Test that a success message is shown when switching."""
        user = UserFactory()
        org = OrganizationFactory(name="Test Org")
        OrganizationMemberFactory(user=user, organization=org)
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": org.id}),
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "selected" in str(messages[0]).lower()
        assert "Test Org" in str(messages[0])

    def test_prevents_switching_to_unauthorized_organization(self, client):
        """Test that user cannot switch to an organization they don't belong to."""
        user = UserFactory()
        org = OrganizationFactory()
        # User is not a member of this organization
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": org.id}),
            follow=True,
        )

        # Should redirect to dashboard
        assert response.status_code == 200

        # Should show error message
        messages = list(get_messages(response.wsgi_request))
        error_messages = [m for m in messages if "error" in m.tags]
        assert len(error_messages) > 0
        assert "access" in str(error_messages[0]).lower()

    def test_handles_nonexistent_organization(self, client):
        """Test that switching to a non-existent organization shows an error."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": 99999}),
            follow=True,
        )

        assert response.status_code == 200

        messages = list(get_messages(response.wsgi_request))
        error_messages = [m for m in messages if "error" in m.tags]
        assert len(error_messages) > 0

    def test_redirects_to_dashboard(self, client):
        """Test that after switching, user is redirected to dashboard."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org)
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(
            reverse("organization:switch", kwargs={"organization_id": org.id})
        )

        assert response.status_code == 302
        assert response.url == reverse("dashboard")
