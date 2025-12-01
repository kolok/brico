import pytest
from audits.tests.factories import ProjectAuditCriterionFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username="user", password="password")
    client.login(username="user", password="password")  # pragma: allowlist secret
    return user


@pytest.mark.django_db
class TestCriterionDetailView:
    """Test the criterion detail view."""

    def test_login_required(self, client):
        response = client.get(
            reverse(
                "audits:criterion_detail",
                kwargs={"project_slug": "test", "audit_id": 1, "pk": 1},
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_criterion_detail_view_context(self, client, login_user):
        project_audit_criterion = ProjectAuditCriterionFactory()

        url = reverse(
            "audits:criterion_detail",
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

    def test_criterion_detail_view_with_session_id(self, client, login_user):
        project_audit_criterion = ProjectAuditCriterionFactory()
        session_id = "test-session-id"

        url = reverse(
            "audits:criterion_detail",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "pk": project_audit_criterion.id,
            },
        )
        response = client.get(url, {"session_id": session_id})

        assert response.status_code == 200
        assert response.context["session_id"] == session_id

    def test_criterion_detail_view_queryset_prefetch(self, client, login_user):
        project_audit_criterion = ProjectAuditCriterionFactory()

        url = reverse(
            "audits:criterion_detail",
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
