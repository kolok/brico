import pytest
from django.db import IntegrityError
from django.utils import timezone
from organization.models.organization import Organization, Project, Resource


@pytest.mark.django_db
class TestOrganization:
    def test_slug_generation_automatic(self):
        org = Organization.objects.create(name="Organisation & Co. (2024)")

        assert org.slug == "organisation-co-2024"

    def test_name_uniqueness(self):
        Organization.objects.create(name="Organisation Unique")

        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Organisation Unique")

    def test_slug_uniqueness(self):
        org1 = Organization.objects.create(name="Test Organisation")
        org2 = Organization.objects.create(name="Test-Organisation")

        assert org1.slug == "test-organisation"
        assert org2.slug != org1.slug
        assert org2.slug.startswith("test-organisation")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            Organization.objects.create(name=None)

    def test_str_representation(self):
        org = Organization.objects.create(name="Mon Organisation")

        assert str(org) == "Mon Organisation"


@pytest.fixture
def organization():
    return Organization.objects.create(name="Mon Organisation")


@pytest.mark.django_db
class TestProject:
    def test_slug_generation_automatic(self, organization):
        project = Project.objects.create(
            name="Mon Projet & Co. (2024)", organization=organization
        )

        assert project.slug == "mon-projet-co-2024"

    def test_name_uniqueness(self, organization):
        Project.objects.create(name="Projet Unique", organization=organization)

        with pytest.raises(IntegrityError):
            Project.objects.create(name="Projet Unique", organization=organization)

    def test_organization_foreign_key(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)

        assert project.organization == organization
        assert project in organization.projects.all()

    def test_cascade_delete(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)
        project_id = project.id

        organization.delete()

        assert not Project.objects.filter(id=project_id).exists()

    def test_str_representation(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)

        assert str(project) == "Mon Projet"

    def test_description_default_empty(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)

        assert project.description == ""

    def test_organization_projects_relation(self, organization):
        project1 = Project.objects.create(name="Projet 1", organization=organization)
        project2 = Project.objects.create(name="Projet 2", organization=organization)

        assert project1 in organization.projects.all()
        assert project2 in organization.projects.all()
        assert organization.projects.count() == 2

    def test_timestamps_created_at(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)

        assert project.created_at is not None
        assert project.created_at <= timezone.now()

    def test_timestamps_updated_at(self, organization):
        project = Project.objects.create(name="Mon Projet", organization=organization)
        initial_updated_at = project.updated_at

        project.name = "Mon Projet Modifié"
        project.save()

        assert project.updated_at > initial_updated_at


@pytest.fixture
def project(organization):
    return Project.objects.create(name="Mon Projet", organization=organization)


@pytest.mark.django_db
class TestResource:
    def test_resource_type_nullable(self, project):
        """Test que le type peut être None."""
        resource = Resource.objects.create(name="Resource Sans Type", project=project)

        assert resource.type is None

    def test_project_foreign_key(self, project):
        resource = Resource.objects.create(
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.project == project
        assert resource in project.resources.all()

    def test_cascade_delete(self, project):
        resource = Resource.objects.create(
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource_id = resource.id

        project.delete()

        assert not Resource.objects.filter(id=resource_id).exists()

    def test_cascade_delete_full_hierarchy(self, organization, project):
        """Test la suppression en cascade sur toute la hiérarchie."""
        resource = Resource.objects.create(
            name="Ma Ressource",
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
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert str(resource) == "Ma Ressource"

    def test_description_default_empty(self, project):
        resource = Resource.objects.create(
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.description == ""

    def test_url_field(self, project):
        resource = Resource.objects.create(
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
            url="https://example.com",
        )

        assert resource.url == "https://example.com"

    def test_url_default_empty(self, project):
        """Test que l'URL peut être vide."""
        resource = Resource.objects.create(
            name="Ma Ressource",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )

        assert resource.url == ""

    def test_project_resources_relation(self, project):
        resource1 = Resource.objects.create(
            name="Ressource 1",
            type=Resource.ResourceType.FRONTEND_CODE,
            project=project,
        )
        resource2 = Resource.objects.create(
            name="Ressource 2",
            type=Resource.ResourceType.BACKEND_CODE,
            project=project,
        )

        assert resource1 in project.resources.all()
        assert resource2 in project.resources.all()
        assert project.resources.count() == 2
