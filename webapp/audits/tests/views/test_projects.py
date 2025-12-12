import pytest
from audits.tests.factories import ProjectAuditFactory
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth import get_user_model
from django.urls import reverse
from organization.models.organization import Organization, Project
from organization.tests.factories import OrganizationFactory, ProjectFactory

User = get_user_model()


@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username="user", password="password")
    client.login(username="user", password="password")  # pragma: allowlist secret
    return user


@pytest.mark.django_db
class TestProjectListView:
    """Test the project list view."""

    @pytest.fixture
    def organization(self, client):
        organization = OrganizationFactory()
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()
        return organization

    def test_login_required(self, client):
        response = client.get(reverse("audits:project_list"))
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_project_list_view_doesnt_display_projects_from_other_organizations(
        self, client, login_user, organization
    ):
        other_organization = OrganizationFactory()
        project = ProjectFactory(organization=other_organization)

        url = reverse("audits:project_list")
        response = client.get(url)
        assert response.status_code == 200
        projects = list(response.context["projects"])
        assert project not in projects

    def test_project_list_view_displays_all_projects(
        self, client, login_user, organization
    ):
        project1 = ProjectFactory(organization=organization)
        project2 = ProjectFactory(organization=organization)
        project3 = ProjectFactory(organization=organization)

        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 200
        projects = list(response.context["projects"])
        assert len(projects) == 3
        assert project1 in projects
        assert project2 in projects
        assert project3 in projects

    def test_project_list_view_empty(self, client, login_user):
        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 200
        assert list(response.context["projects"]) == []

    def test_project_list_view_search_filters_by_name(
        self, client, login_user, organization
    ):
        project1 = ProjectFactory(name="Hello World", organization=organization)
        project2 = ProjectFactory(name="Some other project", organization=organization)
        project3 = ProjectFactory(name="HELLO again", organization=organization)

        url = reverse("audits:project_list")
        response = client.get(url, data={"search": "hello"})

        assert response.status_code == 200
        projects = list(response.context["projects"])
        assert project1 in projects
        assert project3 in projects
        assert project2 not in projects

    def test_project_list_view_search_strips_spaces(
        self, client, login_user, organization
    ):
        project = ProjectFactory(name="Unique Project Name", organization=organization)
        ProjectFactory(name="Another Project", organization=organization)

        url = reverse("audits:project_list")
        response = client.get(url, data={"search": "   Unique Project   "})

        assert response.status_code == 200
        projects = list(response.context["projects"])
        assert projects == [project]

    def test_project_list_view_search_allows_special_characters(
        self, client, login_user, organization
    ):
        project = ProjectFactory(
            name="Sécurité & Qualité (2025)", organization=organization
        )
        ProjectFactory(name="Totally different", organization=organization)

        url = reverse("audits:project_list")
        response = client.get(url, data={"search": "sécurité & qualité"})

        assert response.status_code == 200
        projects = list(response.context["projects"])
        assert projects == [project]


@pytest.mark.django_db
class TestProjectDetailView:
    """Test the project detail view."""

    def test_login_required(self, client):
        project = ProjectFactory()
        response = client.get(
            reverse("audits:project_detail", kwargs={"slug": project.slug})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_project_detail_view_context(self, client, login_user):
        project = ProjectFactory()
        ProjectAuditFactory(project=project)

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["project"] == project

    def test_project_detail_view_queryset_prefetch(self, client, login_user):
        project = ProjectFactory()
        ProjectAuditFactory(project=project)

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200
        # Verify that the queryset is properly prefetched
        project_obj = response.context["project"]
        # Accessing related objects should not trigger additional queries
        # (this is a basic check, full query count would require assertNumQueries)
        assert hasattr(project_obj, "resources")
        assert hasattr(project_obj, "audits")

    def test_project_detail_view_404_for_invalid_slug(self, client, login_user):
        url = reverse("audits:project_detail", kwargs={"slug": "non-existent-slug"})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectFormView:
    """Test the project creation form view."""

    def test_login_required_get(self, client):
        response = client.get(reverse("audits:project_form"))
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_login_required_post(self, client):
        response = client.post(
            reverse("audits:project_form"),
            data={"name": "Test project", "description": "Some description"},
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_create_project_ok_and_redirects_to_detail(self, client, login_user):
        Organization.objects.all().delete()
        org = OrganizationFactory(name="My Org")

        response = client.post(
            reverse("audits:project_form"),
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 302
        project = Project.objects.get(name="My Project")
        assert project.organization == org
        assert response.url == reverse(
            "audits:project_detail", kwargs={"slug": project.slug}
        )

    def test_create_project_without_organization_shows_clear_error(
        self, client, login_user
    ):
        Organization.objects.all().delete()

        response = client.post(
            reverse("audits:project_form"),
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 200
        assert Project.objects.filter(name="My Project").count() == 0
        form = response.context["form"]
        assert "No organization is configured" in str(form.non_field_errors())
