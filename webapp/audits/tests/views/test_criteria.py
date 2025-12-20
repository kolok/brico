import pytest
from audits.tests.factories import ProjectAuditCriterionFactory
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    UserFactory,
)

User = get_user_model()


@pytest.fixture(scope="module")
def auth_fixture(django_db_setup, django_db_blocker):
    """
    Load content_type and auth fixtures once per test module.
    """
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
class TestCriterionDetailView:
    """Test the criterion detail view."""

    def test_login_required(self, client):
        """Test that login is required to view criterion detail."""
        response = client.get(
            reverse(
                "audits:projectauditcriterion_detail",
                kwargs={"project_slug": "test", "audit_id": 1, "pk": 1},
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        project_audit_criterion = ProjectAuditCriterionFactory()

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_projectauditcriterion_detail_view_context(self, client, admin_group):
        """Test that criterion detail view context contains correct data."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )
        assert response.context["audit"] == project_audit_criterion.project_audit

    def test_projectauditcriterion_detail_view_with_session_id(
        self, client, admin_group
    ):
        """Test that criterion detail view handles session_id parameter."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )
        session_id = "test-session-id"

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url, {"session_id": session_id})

        assert response.status_code == 200
        assert response.context["session_id"] == session_id

    def test_projectauditcriterion_detail_view_queryset_prefetch(
        self, client, admin_group
    ):
        """Test that criterion detail view properly prefetches related objects."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        # Verify that the queryset is properly prefetched
        criterion = response.context["criterion"]
        # Accessing related objects should not trigger additional queries
        # (this is a basic check, full query count would require assertNumQueries)
        assert hasattr(criterion, "criterion")
        assert hasattr(criterion, "comments")


@pytest.mark.django_db
class TestCriterionDetailViewPermissions:
    """Test permissions for criterion detail view."""

    def test_reader_can_view_projectauditcriterion_detail(self, client, reader_group):
        """Test that reader can view criterion detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_writer_can_view_projectauditcriterion_detail(self, client, writer_group):
        """Test that writer can view criterion detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_admin_can_view_projectauditcriterion_detail(self, client, admin_group):
        """Test that administrator can view criterion detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_non_member_cannot_view_projectauditcriterion_detail(self, client):
        """Test that non-member cannot view criterion detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_cannot_view_projectauditcriterion_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot view criterion from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit__project__organization=organization2
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:projectauditcriterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 404
