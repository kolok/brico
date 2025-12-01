import pytest
from audits.models.audit import ProjectAudit, ProjectAuditCriterion
from audits.tests.factories import (
    AuditLibraryFactory,
    CriterionFactory,
    ProjectAuditFactory,
)
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
class TestAuditDetailView:
    """Test the audit detail view."""

    def test_login_required(self, client):
        response = client.get(
            reverse("audits:audit_detail", kwargs={"project_slug": "test", "pk": 1})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_audit_detail_view_context_contains_project(self, client, login_user):

        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)

        url = reverse(
            "audits:audit_detail",
            kwargs={"project_slug": project.slug, "pk": audit.pk},
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["audit"] == audit
        assert response.context["project"] == project


@pytest.mark.django_db
class TestNewAuditView:
    """Test the new audit view."""

    def test_login_required(self, client):
        response = client.get(
            reverse("audits:new_audit", kwargs={"project_slug": "test"})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_new_audit_view_creates_audit_and_criteria(self, client, login_user):
        project = ProjectFactory()
        audit_library = AuditLibraryFactory()
        # créer quelques critères dans cette librairie
        CriterionFactory.create_batch(3, audit_library=audit_library)

        url = reverse(
            "audits:new_audit",
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
class TestDeleteAuditView:
    """Test the delete audit view."""

    def test_login_required(self, client):
        response = client.get(
            reverse("audits:audit_delete", kwargs={"project_slug": "test", "pk": 1})
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_delete_audit_deletes_instance_and_redirects(self, rf, client, login_user):
        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)

        url = reverse(
            "audits:audit_delete",
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
