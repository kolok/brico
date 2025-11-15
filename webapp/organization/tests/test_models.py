import pytest
from django.db import IntegrityError
from django.utils import timezone
from organization.models.organization import Organization, Project, Resource
from organization.tests.factories import (
    OrganizationFactory,
    ProjectFactory,
    ResourceFactory,
)


@pytest.mark.django_db
class TestOrganization:
    def test_slug_generation_automatic(self):
        org = OrganizationFactory(name="Organization & Co. (2024)")

        assert org.slug == "organization-co-2024"

    def test_name_uniqueness(self):
        OrganizationFactory(name="Unique Organization")

        with pytest.raises(IntegrityError):
            OrganizationFactory(name="Unique Organization")

    def test_slug_uniqueness(self):
        org1 = OrganizationFactory(name="Test Organization")
        org2 = OrganizationFactory(name="Test-Organization")

        assert org1.slug == "test-organization"
        assert org2.slug != org1.slug
        assert org2.slug.startswith("test-organization")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            OrganizationFactory(name=None)

    def test_str_representation(self):
        org = OrganizationFactory(name="My Organization")

        assert str(org) == "My Organization"


@pytest.fixture
def organization():
    return OrganizationFactory()


@pytest.mark.django_db
class TestProject:
    def test_slug_generation_automatic(self, organization):
        project = ProjectFactory(
            name="My Project & Co. (2024)", organization=organization
        )

        assert project.slug == "my-project-co-2024"

    def test_slug_uniqueness(self, organization):
        project1 = ProjectFactory(name="Unique Project", organization=organization)
        slug1 = project1.slug

        organization2 = OrganizationFactory(name="Other Organization")
        project2 = ProjectFactory(name="Unique Project", organization=organization2)
        slug2 = project2.slug

        assert slug1 == slug2
        assert slug1 == "unique-project"

    def test_name_uniqueness_per_organization(self, organization):
        ProjectFactory(name="Unique Project", organization=organization)

        with pytest.raises(IntegrityError):
            ProjectFactory(name="Unique Project", organization=organization)

    def test_organization_foreign_key(self, organization):
        project = ProjectFactory(organization=organization)

        assert project.organization == organization
        assert project in organization.projects.all()

    def test_cascade_delete(self, organization):
        project = ProjectFactory(organization=organization)
        project_id = project.id

        organization.delete()

        assert not Project.objects.filter(id=project_id).exists()

    def test_str_representation(self, organization):
        project = ProjectFactory(name="My Project", organization=organization)

        assert str(project) == "My Project"

    def test_description_default_empty(self, organization):
        project = ProjectFactory(organization=organization, description="")

        assert project.description == ""

    def test_organization_projects_relation(self, organization):
        project1 = ProjectFactory(name="Project 1", organization=organization)
        project2 = ProjectFactory(name="Project 2", organization=organization)

        assert project1 in organization.projects.all()
        assert project2 in organization.projects.all()
        assert organization.projects.count() == 2

    def test_timestamps_created_at(self, organization):
        project = ProjectFactory(organization=organization)

        assert project.created_at is not None
        assert project.created_at <= timezone.now()

    def test_timestamps_updated_at(self, organization):
        project = ProjectFactory(organization=organization)
        initial_updated_at = project.updated_at

        project.name = "My Modified Project"
        project.save()

        assert project.updated_at > initial_updated_at


@pytest.fixture
def project(organization):
    return ProjectFactory(organization=organization)


@pytest.mark.django_db
class TestResource:
    def test_resource_type_cant_be_null(self, project):
        with pytest.raises(IntegrityError):
            ResourceFactory(type=None, project=project)

    def test_project_foreign_key(self, project):
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.project == project
        assert resource in project.resources.all()

    def test_cascade_delete(self, project):
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource_id = resource.id

        project.delete()

        assert not Resource.objects.filter(id=resource_id).exists()

    def test_cascade_delete_full_hierarchy(self, organization, project):
        """Test cascade deletion across the entire hierarchy."""
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource_id = resource.id

        organization.delete()

        assert not Organization.objects.filter(id=organization.id).exists()
        assert not Project.objects.filter(id=project.id).exists()
        assert not Resource.objects.filter(id=resource_id).exists()

    def test_str_representation(self, project):
        resource = ResourceFactory(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert str(resource) == "My Resource"

    def test_description_default_empty(self, project):
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
            description="",
        )

        assert resource.description == ""

    def test_url_field(self, project):
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
            url="https://example.com",
        )

        assert resource.url == "https://example.com"

    def test_url_default_empty(self, project):
        """Test that the URL can be empty."""
        resource = ResourceFactory(
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
            url="",
        )

        assert resource.url == ""

    def test_project_resources_relation(self, project):
        resource1 = ResourceFactory(
            name="Resource 1",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource2 = ResourceFactory(
            name="Resource 2",
            type=Resource.ResourceType.BACKEND_CODE,
            project=project,
        )

        assert resource1 in project.resources.all()
        assert resource2 in project.resources.all()
        assert project.resources.count() == 2
