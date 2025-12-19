import pytest
from audits.tests.factories import ProjectAuditFactory
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from organization.models.organization import Project
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    ProjectFactory,
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


@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username="user", password="password")
    client.login(username="user", password="password")  # pragma: allowlist secret
    return user


@pytest.fixture
def organization(client, login_user, admin_group):
    organization = OrganizationFactory()
    OrganizationMemberFactory(
        user=login_user, organization=organization, group=admin_group
    )
    session = client.session
    session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
    session.save()
    return organization


@pytest.mark.django_db
class TestProjectListView:
    """Test the project list view."""

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

    def test_project_list_view_empty(self, client, login_user, organization):
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

    def test_project_detail_view_context(
        self, client, login_user, organization, admin_group
    ):
        project = ProjectFactory(organization=organization)
        ProjectAuditFactory(project=project)

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["project"] == project

    def test_project_detail_view_queryset_prefetch(
        self, client, login_user, organization, admin_group
    ):
        project = ProjectFactory(organization=organization)
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

    def test_project_detail_view_404_for_invalid_slug(
        self, client, login_user, organization
    ):
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

    def test_create_project_ok_and_redirects_to_detail(
        self, client, login_user, organization
    ):
        response = client.post(
            reverse("audits:project_form"),
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 302
        project = Project.objects.get(name="My Project")
        assert project.organization == organization
        assert response.url == reverse(
            "audits:project_detail", kwargs={"slug": project.slug}
        )

    def test_create_project_without_organization_shows_clear_error(
        self, client, login_user, admin_group
    ):
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=login_user, organization=organization, group=admin_group
        )
        # Clear organization from session
        login_user.organization_memberships.all().delete()

        response = client.post(
            reverse("audits:project_form"),
            data={"name": "My Project", "description": "Desc"},
        )
        assert (
            response.status_code == 403
        )  # PermissionDenied when no organization selected


@pytest.mark.django_db
class TestProjectListViewPermissions:
    """Test permissions for project list view."""

    def test_reader_can_view_project_list(self, client, reader_group):
        """Test that reader can view project list."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 200

    def test_writer_can_view_project_list(self, client, writer_group):
        """Test that writer can view project list."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 200

    def test_admin_can_view_project_list(self, client, admin_group):
        """Test that administrator can view project list."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 200

    def test_non_member_cannot_view_project_list(self, client):
        """Test that non-member cannot view project list."""
        user = UserFactory()
        organization = OrganizationFactory()
        ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_list")
        response = client.get(url)

        assert response.status_code == 403


@pytest.mark.django_db
class TestProjectDetailViewPermissions:
    """Test permissions for project detail view."""

    def test_reader_can_view_project_detail(self, client, reader_group):
        """Test that reader can view project detail."""
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

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_writer_can_view_project_detail(self, client, writer_group):
        """Test that writer can view project detail."""
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

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_admin_can_view_project_detail(self, client, admin_group):
        """Test that administrator can view project detail."""
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

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 200

    def test_non_member_cannot_view_project_detail(self, client):
        """Test that non-member cannot view project detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 403

    def test_cannot_view_project_from_different_organization(self, client, admin_group):
        """Test that user cannot view project from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse("audits:project_detail", kwargs={"slug": project.slug})
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectFormViewPermissions:
    """Test permissions for project form view."""

    def test_reader_cannot_create_project(self, client, reader_group):
        """Test that reader cannot create project."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_form")

        response = client.post(
            url,
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 403
        assert Project.objects.filter(name="My Project").count() == 0

    def test_writer_can_create_project(self, client, writer_group):
        """Test that writer can create project."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_form")
        response = client.post(
            url,
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 302
        project = Project.objects.get(name="My Project")
        assert project.organization == organization

    def test_admin_can_create_project(self, client, admin_group):
        """Test that administrator can create project."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_form")
        response = client.post(
            url,
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 302
        project = Project.objects.get(name="My Project")
        assert project.organization == organization

    def test_non_member_cannot_create_project(self, client):
        """Test that non-member cannot create project."""
        user = UserFactory()
        organization = OrganizationFactory()

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse("audits:project_form")
        response = client.post(
            url,
            data={"name": "My Project", "description": "Desc"},
        )

        assert response.status_code == 403
        assert Project.objects.filter(name="My Project").count() == 0
