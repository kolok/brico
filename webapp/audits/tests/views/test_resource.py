import pytest
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from organization.models.organization import Resource
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    ProjectFactory,
    ResourceFactory,
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
class TestResourceDetailView:
    """Test the resource detail view."""

    def test_login_required(self, client):
        """Test that login is required to view resource detail."""
        project = ProjectFactory()
        resource = ResourceFactory(project=project)
        response = client.get(
            reverse(
                "audits:resource_detail",
                kwargs={"project_slug": project.slug, "pk": resource.pk},
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_resource_detail_view_context_contains_project_and_resource(
        self, client, admin_group
    ):
        """Test that resource detail view context contains project and resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["resource"] == resource
        assert response.context["project"] == project

    def test_cannot_view_resource_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot view resource from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestResourceDetailViewPermissions:
    """Test permissions for resource detail view."""

    def test_reader_can_view_resource_detail(self, client, reader_group):
        """Test that reader can view resource detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_writer_can_view_resource_detail(self, client, writer_group):
        """Test that writer can view resource detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_admin_can_view_resource_detail(self, client, admin_group):
        """Test that administrator can view resource detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_non_member_cannot_view_resource_detail(self, client):
        """Test that non-member cannot view resource detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_detail",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 403


@pytest.mark.django_db
class TestNewResourceView:
    """Test the new resource view."""

    def test_login_required(self, client):
        """Test that login is required to create resource."""
        project = ProjectFactory()
        response = client.get(
            reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        # No organization in session

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 403

    def test_resource_new_view_creates_resource_and_redirects(
        self, client, admin_group
    ):
        """
        Test that new resource view creates resource and redirects to project detail.
        """
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 302
        resource = Resource.objects.get(name="Test Resource")
        assert resource.project == project
        assert response.url == reverse(
            "audits:project_detail", kwargs={"slug": project.slug}
        )

    def test_resource_new_view_context_contains_project(self, client, admin_group):
        """Test that new resource view context contains project."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["project"] == project


@pytest.mark.django_db
class TestNewResourceViewPermissions:
    """Test permissions for new resource view."""

    def test_reader_cannot_create_resource(self, client, reader_group):
        """Test that reader cannot create resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 403
        assert Resource.objects.filter(name="Test Resource").count() == 0

    def test_writer_can_create_resource(self, client, writer_group):
        """Test that writer can create resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 302
        resource = Resource.objects.get(name="Test Resource")
        assert resource.project == project

    def test_admin_can_create_resource(self, client, admin_group):
        """Test that administrator can create resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 302
        resource = Resource.objects.get(name="Test Resource")
        assert resource.project == project

    def test_non_member_cannot_create_resource(self, client):
        """Test that non-member cannot create resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:resource_new", kwargs={"project_slug": project.slug})
        response = client.post(
            url,
            data={
                "name": "Test Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com",
                "description": "Test description",
            },
        )

        assert response.status_code == 403
        assert Resource.objects.filter(name="Test Resource").count() == 0


@pytest.mark.django_db
class TestEditResourceView:
    """Test the edit resource view."""

    def test_login_required(self, client):
        """Test that login is required to edit resource."""
        project = ProjectFactory()
        resource = ResourceFactory(project=project)
        response = client.get(
            reverse(
                "audits:resource_edit",
                kwargs={"project_slug": project.slug, "pk": resource.pk},
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 403

    def test_resource_edit_view_updates_resource_and_redirects(
        self, client, admin_group
    ):
        """
        Test that edit resource view updates resource and redirects to project detail.
        """
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project, name="Original Name")

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 302
        resource.refresh_from_db()
        assert resource.name == "Updated Resource"
        assert response.url == reverse(
            "audits:project_detail", kwargs={"slug": project.slug}
        )

    def test_resource_edit_view_context_contains_project_and_resource(
        self, client, admin_group
    ):
        """Test that edit resource view context contains project and resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["resource"] == resource
        assert response.context["project"] == project

    def test_cannot_edit_resource_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot edit resource from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestEditResourceViewPermissions:
    """Test permissions for edit resource view."""

    def test_reader_cannot_edit_resource(self, client, reader_group):
        """Test that reader cannot edit resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project, name="Original Name")

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 403
        resource.refresh_from_db()
        assert resource.name == "Original Name"

    def test_writer_can_edit_resource(self, client, writer_group):
        """Test that writer can edit resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project, name="Original Name")

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 302
        resource.refresh_from_db()
        assert resource.name == "Updated Resource"

    def test_admin_can_edit_resource(self, client, admin_group):
        """Test that administrator can edit resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project, name="Original Name")

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 302
        resource.refresh_from_db()
        assert resource.name == "Updated Resource"

    def test_non_member_cannot_edit_resource(self, client):
        """Test that non-member cannot edit resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project, name="Original Name")

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_edit",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(
            url,
            data={
                "name": "Updated Resource",
                "type": Resource.ResourceType.TECHNICAL_DOCUMENTATION,
                "url": "https://example.com/updated",
                "description": "Updated description",
            },
        )

        assert response.status_code == 403
        resource.refresh_from_db()
        assert resource.name == "Original Name"


@pytest.mark.django_db
class TestDeleteResourceView:
    """Test the delete resource view."""

    def test_login_required(self, client):
        """Test that login is required to delete resource."""
        project = ProjectFactory()
        resource = ResourceFactory(project=project)
        response = client.post(
            reverse(
                "audits:resource_delete",
                kwargs={"project_slug": project.slug, "pk": resource.pk},
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 403

    def test_resource_delete_view_deletes_resource_and_redirects(
        self, client, admin_group
    ):
        """
        Test that delete resource view deletes resource and redirects to project detail.
        """
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 302
        assert not Resource.objects.filter(pk=resource.pk).exists()
        assert response.url == reverse(
            "audits:project_detail", kwargs={"slug": project.slug}
        )

    def test_resource_delete_view_context_contains_project_and_resource(
        self, client, admin_group
    ):
        """Test that delete resource view context contains project and resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["resource"] == resource
        assert response.context["project"] == project

    def test_cannot_delete_resource_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot delete resource from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 404
        assert Resource.objects.filter(pk=resource.pk).exists()


@pytest.mark.django_db
class TestDeleteResourceViewPermissions:
    """Test permissions for delete resource view."""

    def test_reader_cannot_delete_resource(self, client, reader_group):
        """Test that reader cannot delete resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 403
        assert Resource.objects.filter(pk=resource.pk).exists()

    def test_writer_can_delete_resource(self, client, writer_group):
        """Test that writer can delete resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 302
        assert not Resource.objects.filter(pk=resource.pk).exists()

    def test_admin_can_delete_resource(self, client, admin_group):
        """Test that administrator can delete resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 302
        assert not Resource.objects.filter(pk=resource.pk).exists()

    def test_non_member_cannot_delete_resource(self, client):
        """Test that non-member cannot delete resource."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        resource = ResourceFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:resource_delete",
            kwargs={"project_slug": project.slug, "pk": resource.pk},
        )
        response = client.post(url)

        assert response.status_code == 403
        assert Resource.objects.filter(pk=resource.pk).exists()
