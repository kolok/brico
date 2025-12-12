import pytest
from core.middleware import ORGANIZATIONS_SESSION_KEY
from django.contrib.auth import get_user_model
from django.urls import reverse
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    UserFactory,
)

User = get_user_model()


@pytest.mark.django_db
class TestIndexView:
    def test_authenticated_user_is_redirected_to_dashboard(self, client):
        User.objects.create_user(
            username="user", password="password"  # pragma: allowlist secret
        )
        client.login(username="user", password="password")  # pragma: allowlist secret

        response = client.get(reverse("index"))

        assert response.status_code == 302
        assert response.url == reverse("dashboard")

    def test_unauthenticated_user_sees_index_page(self, client):
        """Test that unauthenticated users can see the index page."""
        response = client.get(reverse("index"))

        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardView:
    def test_redirects_when_not_authenticated(self, client):
        """Test that unauthenticated users are redirected (to login or create)."""
        response = client.get(reverse("dashboard"), follow=False)

        # LoginRequiredMixin redirects (exact URL depends on configuration)
        assert response.status_code == 302
        # Should redirect to login page (may include next parameter)
        assert response.url.startswith(reverse("account_login"))

    def test_redirects_to_organization_create_when_no_organizations(self, client):
        """Test that users without organizations are redirected to create one."""
        user = UserFactory()
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        response = client.get(reverse("dashboard"))

        assert response.status_code == 302
        assert response.url == reverse("organization:create")

    def test_shows_dashboard_when_user_has_organizations(self, client):
        """Test that dashboard is shown when user has organizations."""
        user = UserFactory()
        org = OrganizationFactory()
        OrganizationMemberFactory(user=user, organization=org)
        client.login(
            username=user.username, password="password"  # pragma: allowlist secret
        )

        # Set session manually since middleware might not run in tests
        session = client.session
        session[ORGANIZATIONS_SESSION_KEY] = [(org.id, org.name)]
        session.save()

        response = client.get(reverse("dashboard"))

        assert response.status_code == 200
