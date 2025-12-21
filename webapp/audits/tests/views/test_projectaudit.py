import pytest
from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from audits.tests.factories import (
    AuditLibraryFactory,
    CriterionFactory,
    ProjectAuditFactory,
    UserFactory,
)
from core.middleware import CURRENT_ORGANIZATION_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from organization.tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    ProjectFactory,
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
class TestProjectAuditDetailView:
    """Test the audit detail view."""

    def test_login_required(self, client):
        """Test that login is required to view audit detail."""
        response = client.get(
            reverse(
                "audits:projectaudit_detail", kwargs={"project_slug": "test", "pk": 1}
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_projectaudit_detail_view_context_contains_project(
        self, client, admin_group
    ):
        """Test that audit detail view context contains project."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["audit"] == audit
        assert response.context["project"] == project


@pytest.mark.django_db
class TestProjectAuditDetailViewPermissions:
    """Test permissions for project audit detail view."""

    def test_reader_can_view_projectaudit_detail(self, client, reader_group):
        """Test that reader can view project audit detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_writer_can_view_projectaudit_detail(self, client, writer_group):
        """Test that writer can view project audit detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_admin_can_view_projectaudit_detail(self, client, admin_group):
        """Test that administrator can view project audit detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200

    def test_non_member_cannot_view_projectaudit_detail(self, client):
        """Test that non-member cannot view project audit detail."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_cannot_view_projectaudit_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot view project audit from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:projectaudit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 404


@pytest.mark.django_db
class TestNewProjectAuditView:
    """Test the new audit view."""

    def test_login_required(self, client):
        """Test that login is required to create audit."""
        response = client.get(
            reverse("audits:projectaudit_new", kwargs={"project_slug": "test"})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )
        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
        )

        assert response.status_code == 403

    def test_projectaudit_new_view_creates_audit_and_criteria(
        self, client, admin_group
    ):
        """Test that new projectaudit view creates audit and criteria."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)
        # créer quelques critères dans cette librairie
        CriterionFactory.create_batch(3, audit_library=audit_library)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )

        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
            follow=True,
        )

        assert response.status_code == 200

        # vérifier que l'audit a été créé
        project_audit = ProjectAudit.objects.get(
            project=project, audit_library=audit_library
        )

        # vérifier que les critères liés ont été créés
        assert (
            ProjectAuditCriterion.objects.filter(project_audit=project_audit).count()
            == 3
        )

        # vérifie la redirection vers la page du projet
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse("audits:project_detail", kwargs={"slug": project.slug})
            in last_redirect_url
        )


@pytest.mark.django_db
class TestNewProjectAuditViewPermissions:
    """Test permissions for new project audit view."""

    def test_reader_can_view_projectaudit_new_form_but_cannot_submit(
        self, client, reader_group
    ):
        """Test that reader can view new project audit form but cannot submit it."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )
        # Reader can view the form (GET uses view_projectaudit permission)
        response = client.get(url)
        assert response.status_code == 200

        # But cannot submit it (POST uses add_projectaudit permission)
        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
        )
        assert response.status_code == 403

    def test_writer_can_view_projectaudit_new_form(self, client, writer_group):
        """Test that writer can view new project audit form."""
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

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "project" in response.context
        assert response.context["project"] == project

    def test_admin_can_view_projectaudit_new_form(self, client, admin_group):
        """Test that administrator can view new project audit form."""
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

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "project" in response.context
        assert response.context["project"] == project

    def test_non_member_cannot_view_projectaudit_new_form(self, client):
        """Test that non-member cannot view new project audit form."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_reader_cannot_create_projectaudit(self, client, reader_group):
        """Test that reader cannot create project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )

        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
        )

        assert response.status_code == 403

    def test_writer_can_create_projectaudit(self, client, writer_group):
        """Test that writer can create project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )

        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
            follow=True,
        )

        assert response.status_code == 200
        assert ProjectAudit.objects.filter(
            project=project, audit_library=audit_library
        ).exists()

    def test_admin_can_create_projectaudit(self, client, admin_group):
        """Test that administrator can create project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )

        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
            follow=True,
        )

        assert response.status_code == 200
        assert ProjectAudit.objects.filter(
            project=project, audit_library=audit_library
        ).exists()

    def test_non_member_cannot_create_projectaudit(self, client):
        """Test that non-member cannot create project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit_library = AuditLibraryFactory(organization=organization)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_new",
            kwargs={"project_slug": project.slug},
        )

        response = client.post(
            url,
            data={
                "audit_library": audit_library.pk,
            },
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestDeleteProjectAuditView:
    """Test the delete audit view."""

    def test_login_required(self, client):
        """Test that login is required to delete audit."""
        response = client.get(
            reverse(
                "audits:projectaudit_delete", kwargs={"project_slug": "test", "pk": 1}
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_organization_required(self, client):
        """Test that organization selection is required."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        # No organization in session

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url)

        assert response.status_code == 403

    def test_delete_projectaudit_deletes_instance_and_redirects(
        self, client, admin_group
    ):
        """Test that delete audit deletes instance and redirects."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )

        # On passe par le client pour vérifier le comportement global
        response = client.post(url, follow=True)

        assert response.status_code == 200
        # l'audit doit être supprimé
        assert not ProjectAudit.objects.filter(pk=audit.pk).exists()

        # vérifier la redirection finale
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse("audits:project_detail", kwargs={"slug": project.slug})
            in last_redirect_url
        )


@pytest.mark.django_db
class TestDeleteProjectAuditViewPermissions:
    """Test permissions for delete project audit view."""

    def test_reader_can_view_delete_projectaudit_form_but_cannot_submit(
        self, client, reader_group
    ):
        """Test that reader can view delete confirmation page but cannot submit it."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        # Reader can view the confirmation page (GET uses view_projectaudit permission)
        response = client.get(url)
        assert response.status_code == 403

        # But cannot submit deletion (POST uses delete_projectaudit permission)
        response = client.post(url)
        assert response.status_code == 403
        # l'audit ne doit pas être supprimé
        assert ProjectAudit.objects.filter(pk=audit.pk).exists()

    def test_writer_can_view_delete_projectaudit_form(self, client, writer_group):
        """Test that writer can view delete project audit confirmation page."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "project" in response.context
        assert response.context["project"] == project
        assert "projectaudit" in response.context or "object" in response.context

    def test_admin_can_view_delete_projectaudit_form(self, client, admin_group):
        """Test that administrator can view delete project audit confirmation page."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "project" in response.context
        assert response.context["project"] == project
        assert "projectaudit" in response.context or "object" in response.context

    def test_non_member_cannot_view_delete_projectaudit_form(self, client):
        """Test that non-member cannot view delete project audit confirmation page."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 403

    def test_reader_cannot_delete_projectaudit(self, client, reader_group):
        """Test that reader cannot delete project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=reader_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url)

        assert response.status_code == 403
        # l'audit ne doit pas être supprimé
        assert ProjectAudit.objects.filter(pk=audit.pk).exists()

    def test_writer_can_delete_projectaudit(self, client, writer_group):
        """Test that writer can delete project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=writer_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url, follow=True)

        assert response.status_code == 200
        assert not ProjectAudit.objects.filter(pk=audit.pk).exists()

    def test_admin_can_delete_projectaudit(self, client, admin_group):
        """Test that administrator can delete project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization, group=admin_group
        )
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url, follow=True)

        assert response.status_code == 200
        assert not ProjectAudit.objects.filter(pk=audit.pk).exists()

    def test_non_member_cannot_delete_projectaudit(self, client):
        """Test that non-member cannot delete project audit."""
        user = UserFactory()
        organization = OrganizationFactory()
        project = ProjectFactory(organization=organization)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (organization.id, organization.name)
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url)

        assert response.status_code == 403
        # l'audit ne doit pas être supprimé
        assert ProjectAudit.objects.filter(pk=audit.pk).exists()

    def test_cannot_delete_projectaudit_from_different_organization(
        self, client, admin_group
    ):
        """Test that user cannot delete project audit from different organization."""
        user = UserFactory()
        organization1 = OrganizationFactory()
        organization2 = OrganizationFactory()
        OrganizationMemberFactory(
            user=user, organization=organization1, group=admin_group
        )
        project = ProjectFactory(organization=organization2)
        audit = ProjectAuditFactory(project=project)

        client.force_login(user)
        session = client.session
        session[CURRENT_ORGANIZATION_SESSION_KEY] = (
            organization1.id,
            organization1.name,
        )
        session.save()

        url = reverse(
            "audits:projectaudit_delete",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.post(url)

        assert response.status_code == 404
        # l'audit ne doit pas être supprimé
        assert ProjectAudit.objects.filter(pk=audit.pk).exists()
