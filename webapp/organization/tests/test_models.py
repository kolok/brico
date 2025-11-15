import pytest
from django.db import IntegrityError
from django.utils import timezone
from organization.models.organization import Organization, Project, Resource


@pytest.mark.django_db
class TestOrganization:
    def test_slug_generation_automatic(self):
        org = Organization.objects.create(name="Organization & Co. (2024)")

        assert org.slug == "organization-co-2024"

    def test_name_uniqueness(self):
        Organization.objects.create(name="Unique Organization")

        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Unique Organization")

    def test_slug_uniqueness(self):
        org1 = Organization.objects.create(name="Test Organization")
        org2 = Organization.objects.create(name="Test-Organization")

        assert org1.slug == "test-organization"
        assert org2.slug != org1.slug
        assert org2.slug.startswith("test-organization")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            Organization.objects.create(name=None)

    def test_str_representation(self):
        org = Organization.objects.create(name="My Organization")

        assert str(org) == "My Organization"


@pytest.fixture
def organization():
    return Organization.objects.create(name="My Organization")


@pytest.mark.django_db
class TestProject:
    def test_slug_generation_automatic(self, organization):
        project = Project.objects.create(
            name="My Project & Co. (2024)", organization=organization
        )

        assert project.slug == "my-project-co-2024"

    def test_slug_uniqueness(self, organization):
        project1 = Project.objects.create(
            name="Unique Project", organization=organization
        )
        slug1 = project1.slug

        organization2 = Organization.objects.create(name="Other Organization")
        project2 = Project.objects.create(
            name="Unique Project", organization=organization2
        )
        slug2 = project2.slug

        assert slug1 == slug2
        assert slug1 == "unique-project"

    def test_name_uniqueness_per_organization(self, organization):
        Project.objects.create(name="Unique Project", organization=organization)

        with pytest.raises(IntegrityError):
            Project.objects.create(name="Unique Project", organization=organization)

    def test_organization_foreign_key(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)

        assert project.organization == organization
        assert project in organization.projects.all()

    def test_cascade_delete(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)
        project_id = project.id

        organization.delete()

        assert not Project.objects.filter(id=project_id).exists()

    def test_str_representation(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)

        assert str(project) == "My Project"

    def test_description_default_empty(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)

        assert project.description == ""

    def test_organization_projects_relation(self, organization):
        project1 = Project.objects.create(name="Project 1", organization=organization)
        project2 = Project.objects.create(name="Project 2", organization=organization)

        assert project1 in organization.projects.all()
        assert project2 in organization.projects.all()
        assert organization.projects.count() == 2

    def test_timestamps_created_at(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)

        assert project.created_at is not None
        assert project.created_at <= timezone.now()

    def test_timestamps_updated_at(self, organization):
        project = Project.objects.create(name="My Project", organization=organization)
        initial_updated_at = project.updated_at

        project.name = "My Modified Project"
        project.save()

        assert project.updated_at > initial_updated_at


@pytest.fixture
def project(organization):
    return Project.objects.create(name="My Project", organization=organization)


@pytest.mark.django_db
class TestResource:
    def test_resource_type_cant_be_null(self, project):
        with pytest.raises(IntegrityError):
            Resource.objects.create(
                name="Resource Without Type", type=None, project=project
            )

    def test_project_foreign_key(self, project):
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.project == project
        assert resource in project.resources.all()

    def test_cascade_delete(self, project):
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource_id = resource.id

        project.delete()

        assert not Resource.objects.filter(id=resource_id).exists()

    def test_cascade_delete_full_hierarchy(self, organization, project):
        """Test cascade deletion across the entire hierarchy."""
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource_id = resource.id

        organization.delete()

        assert not Organization.objects.filter(id=organization.id).exists()
        assert not Project.objects.filter(id=project.id).exists()
        assert not Resource.objects.filter(id=resource_id).exists()

    def test_str_representation(self, project):
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert str(resource) == "My Resource"

    def test_description_default_empty(self, project):
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.description == ""

    def test_url_field(self, project):
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
            url="https://example.com",
        )

        assert resource.url == "https://example.com"

    def test_url_default_empty(self, project):
        """Test that the URL can be empty."""
        resource = Resource.objects.create(
            name="My Resource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.url == ""

    def test_project_resources_relation(self, project):
        resource1 = Resource.objects.create(
            name="Resource 1",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource2 = Resource.objects.create(
            name="Resource 2",
            type=Resource.ResourceType.BACKEND_CODE,
            project=project,
        )

        assert resource1 in project.resources.all()
        assert resource2 in project.resources.all()
        assert project.resources.count() == 2
