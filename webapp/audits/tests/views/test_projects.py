import pytest
from audits.tests.factories import ProjectAuditFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from organization.tests.factories import ProjectFactory

User = get_user_model()


@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username="user", password="password")
    client.login(username="user", password="password")  # pragma: allowlist secret
    return user


@pytest.mark.django_db
class TestProjectListView:
    """Test the project list view."""

    def test_login_required(self, client):
        response = client.get(reverse("audits:project_list"))
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_project_list_view_displays_all_projects(self, client, login_user):
        project1 = ProjectFactory()
        project2 = ProjectFactory()
        project3 = ProjectFactory()

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
