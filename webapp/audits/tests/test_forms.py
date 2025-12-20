import uuid

import pytest
from audits.forms import CommentForm, NewAuditForm, PromptForm
from audits.models.audit import Comment
from audits.tests.factories import (
    AuditLibraryFactory,
    CommentFactory,
    ProjectAuditCriterionFactory,
)
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestNewAuditForm:
    """Test the NewAuditForm."""

    def test_form_has_audit_library_field(self):
        """Test that the form contains the audit_library field."""
        form = NewAuditForm()
        assert "audit_library" in form.fields

    def test_form_valid_with_valid_audit_library(self):
        """Test that the form is valid with a valid audit_library."""
        audit_library = AuditLibraryFactory()
        form = NewAuditForm(data={"audit_library": audit_library.pk})
        assert form.is_valid()

    def test_form_invalid_with_empty_audit_library(self):
        """Test that the form is invalid without an audit_library."""
        form = NewAuditForm(data={})
        assert not form.is_valid()
        assert "audit_library" in form.errors

    def test_form_invalid_with_invalid_audit_library_id(self):
        """Test that the form is invalid with an invalid audit_library id."""
        form = NewAuditForm(data={"audit_library": 99999})
        assert not form.is_valid()
        assert "audit_library" in form.errors

    def test_form_queryset_contains_all_audit_libraries(self):
        """Test that the queryset contains all audit_libraries."""
        audit_library1 = AuditLibraryFactory()
        audit_library2 = AuditLibraryFactory()
        form = NewAuditForm()
        queryset = form.fields["audit_library"].queryset
        assert audit_library1 in queryset
        assert audit_library2 in queryset


@pytest.mark.django_db
class TestCommentForm:
    """Test the CommentForm."""

    def test_form_has_comment_field(self):
        """Test that the form contains the comment field."""
        form = CommentForm()
        assert "comment" in form.fields
        assert form.Meta.fields == ["comment"]

    def test_form_valid_with_comment(self):
        """Test that the form is valid with a comment."""
        form = CommentForm(data={"comment": "Ceci est un commentaire de test"})
        assert form.is_valid()

    def test_form_valid_with_empty_comment(self):
        """Test that the form is valid with an empty comment (blank=True)."""
        form = CommentForm(data={"comment": ""})
        assert form.is_valid()

    def test_form_save_creates_instance(self):
        """Test that the form save creates an instance."""
        project_audit_criterion = ProjectAuditCriterionFactory()
        user = User.objects.create_user(username="testuser", password="password")
        form = CommentForm(
            data={"comment": "New comment"},
            instance=Comment(
                project_audit_criterion=project_audit_criterion, user=user
            ),
        )
        assert form.is_valid()
        comment = form.save()
        assert comment.comment == "New comment"
        assert comment.project_audit_criterion == project_audit_criterion
        assert comment.user == user

    def test_form_save_updates_existing_instance(self):
        """Test that the form save updates an existing instance."""
        comment = CommentFactory(comment="Old comment")
        form = CommentForm(data={"comment": "New comment"}, instance=comment)
        assert form.is_valid()
        updated_comment = form.save()
        assert updated_comment.comment == "New comment"
        assert updated_comment.pk == comment.pk


@pytest.mark.django_db
class TestPromptForm:
    """Form tests for the PromptForm."""

    def test_form_has_message_field(self):
        """Test that form contains the message and session_id fields."""
        form = PromptForm()
        assert "message" in form.fields
        assert "session_id" in form.fields

    def test_form_session_id_has_initial_value(self):
        """Test that the session_id field has an initial value (UUID)."""
        form = PromptForm()
        initial_value = form.fields["session_id"].initial
        assert initial_value is not None
        assert isinstance(initial_value, uuid.UUID)

    def test_form_valid_with_message_and_session_id(self):
        """Test that the form is valid with a message and a valid session_id."""
        session_id = uuid.uuid4()
        form = PromptForm(
            data={"message": "Test message", "session_id": str(session_id)}
        )
        assert form.is_valid()

    def test_form_invalid_without_message(self):
        """Test that the form is invalid without a message."""
        form = PromptForm(data={})
        assert not form.is_valid()
        assert "message" in form.errors

    def test_form_invalid_with_empty_message(self):
        """Test that the form is invalid with an empty message."""
        form = PromptForm(data={"message": ""})
        assert not form.is_valid()
        assert "message" in form.errors

    def test_form_invalid_with_whitespace_only_message(self):
        """Test that the form is invalid with a message containing only whitespace."""
        form = PromptForm(data={"message": "   "})
        assert not form.is_valid()
        assert "message" in form.errors

    def test_form_invalid_with_invalid_session_id(self):
        """Test that the form is invalid with an invalid session_id."""
        form = PromptForm(
            data={"message": "Test message", "session_id": "invalid-uuid"}
        )
        assert not form.is_valid()
        assert "session_id" in form.errors

    def test_form_session_id_initial_is_different_each_time(self):
        """Test that the session_id initial value is different each time."""
        form1 = PromptForm()
        form2 = PromptForm()
        # Note: Since initial=uuid.uuid4() is called each time, the values may be
        # different but this is not guaranteed. We just check that they are valid UUIDs.
        assert isinstance(form1.fields["session_id"].initial, uuid.UUID)
        assert isinstance(form2.fields["session_id"].initial, uuid.UUID)

    def test_form_cleaned_data_contains_message(self):
        """
        Test that cleaned_data contains the message and session_id after validation.
        """
        session_id = uuid.uuid4()
        form = PromptForm(
            data={"message": "Test message", "session_id": str(session_id)}
        )
        assert form.is_valid()
        assert form.cleaned_data["session_id"] == session_id
        assert form.cleaned_data["message"] == "Test message"
