import pytest
from audits.models.audit import ProjectAuditCriterionComment
from audits.tests.factories import (
    ProjectAuditCriterionCommentFactory,
    ProjectAuditCriterionFactory,
)
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username="user", password="password")
    client.login(username="user", password="password")  # pragma: allowlist secret
    return user


@pytest.fixture
def project_audit_criterion():
    """Create a project audit criterion for testing."""
    return ProjectAuditCriterionFactory()


@pytest.mark.django_db
class TestCommentListView:
    """Test the comment list view."""

    def test_login_required(self, client, project_audit_criterion):
        response = client.get(
            reverse(
                "audits:comments_list",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_list_view_context(
        self, client, login_user, project_audit_criterion
    ):
        # Create some comments
        comment1 = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )
        comment2 = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )

        url = reverse(
            "audits:comments_list",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert response.context["audit"] == project_audit_criterion.project_audit
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )
        assert list(response.context["comments"]) == [
            comment2,
            comment1,
        ]  # Ordered by -created_at


@pytest.mark.django_db
class TestCommentCreateView:
    """Test the comment create view."""

    def test_login_required(self, client, project_audit_criterion):
        response = client.get(
            reverse(
                "audits:comment_create",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_create_view_get(self, client, login_user, project_audit_criterion):
        url = reverse(
            "audits:comment_create",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert response.context["audit"] == project_audit_criterion.project_audit
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )

    def test_comment_create_view_post_creates_comment(
        self, client, login_user, project_audit_criterion
    ):
        url = reverse(
            "audits:comment_create",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )

        comment_text = "This is a test comment"
        response = client.post(url, data={"comment": comment_text}, follow=True)

        assert response.status_code == 200

        # Verify comment was created
        comment = ProjectAuditCriterionComment.objects.get(
            project_audit_criterion=project_audit_criterion, user=login_user
        )
        assert comment.comment == comment_text

        # Verify redirect to comments list
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse(
                "audits:comments_list",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
            in last_redirect_url
        )


@pytest.mark.django_db
class TestCommentUpdateView:
    """Test the comment update view."""

    def test_login_required(self, client, project_audit_criterion):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )
        response = client.get(
            reverse(
                "audits:comment_update",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                    "pk": comment.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_update_view_get(self, client, login_user, project_audit_criterion):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion, user=login_user
        )

        url = reverse(
            "audits:comment_update",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert response.context["audit"] == project_audit_criterion.project_audit
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )
        assert response.context["object"] == comment

    def test_comment_update_view_post_updates_comment(
        self, client, login_user, project_audit_criterion
    ):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion,
            user=login_user,
            comment="Original comment",
        )

        url = reverse(
            "audits:comment_update",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )

        updated_text = "Updated comment"
        response = client.post(url, data={"comment": updated_text}, follow=True)

        assert response.status_code == 200

        # Verify comment was updated
        comment.refresh_from_db()
        assert comment.comment == updated_text

        # Verify redirect to comments list
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse(
                "audits:comments_list",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
            in last_redirect_url
        )

    def test_comment_update_view_with_turbo_frame_header(
        self, client, login_user, project_audit_criterion
    ):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion,
            user=login_user,
            comment="Original comment",
        )

        url = reverse(
            "audits:comment_update",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )

        updated_text = "Updated comment"
        response = client.post(
            url,
            data={"comment": updated_text},
            HTTP_TURBO_FRAME="comment-frame",
            follow=True,
        )

        assert response.status_code == 200

        # Verify comment was updated
        comment.refresh_from_db()
        assert comment.comment == updated_text

        # Verify redirect to comment fragment (Turbo Frame)
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse(
                "audits:comment_fragment",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                    "pk": comment.id,
                },
            )
            in last_redirect_url
        )


@pytest.mark.django_db
class TestCommentDeleteView:
    """Test the comment delete view."""

    def test_login_required(self, client, project_audit_criterion):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )
        response = client.get(
            reverse(
                "audits:comment_delete",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                    "pk": comment.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_delete_view_get(self, client, login_user, project_audit_criterion):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion, user=login_user
        )

        url = reverse(
            "audits:comment_delete",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert response.context["audit"] == project_audit_criterion.project_audit
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )
        assert response.context["object"] == comment

    def test_comment_delete_view_post_deletes_comment(
        self, client, login_user, project_audit_criterion
    ):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion, user=login_user
        )
        comment_id = comment.id

        url = reverse(
            "audits:comment_delete",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )

        response = client.post(url, follow=True)

        assert response.status_code == 200

        # Verify comment was deleted
        assert not ProjectAuditCriterionComment.objects.filter(pk=comment_id).exists()

        # Verify redirect to comments list
        assert response.redirect_chain
        last_redirect_url, status = response.redirect_chain[-1]
        assert status == 302
        assert (
            reverse(
                "audits:comments_list",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
            in last_redirect_url
        )


@pytest.mark.django_db
class TestCommentFormCancelView:
    """Test the comment form cancel view."""

    def test_login_required(self, client, project_audit_criterion):
        response = client.get(
            reverse(
                "audits:comment_form_cancel",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_form_cancel_view_renders(
        self, client, login_user, project_audit_criterion
    ):
        url = reverse(
            "audits:comment_form_cancel",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
class TestCommentFragmentView:
    """Test the comment fragment view."""

    def test_login_required(self, client, project_audit_criterion):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )
        response = client.get(
            reverse(
                "audits:comment_fragment",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                    "pk": comment.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_comment_fragment_view_context(
        self, client, login_user, project_audit_criterion
    ):
        comment = ProjectAuditCriterionCommentFactory(
            project_audit_criterion=project_audit_criterion
        )

        url = reverse(
            "audits:comment_fragment",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
                "pk": comment.id,
            },
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["criterion"] == project_audit_criterion
        assert response.context["audit"] == project_audit_criterion.project_audit
        assert (
            response.context["project"] == project_audit_criterion.project_audit.project
        )
        assert response.context["comment"] == comment
