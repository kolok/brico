import uuid
from unittest.mock import mock_open, patch

import pytest
from audits.tests.factories import (
    ProjectAuditCriterionFactory,
    ProjectAuditCriterionPromptFactory,
)
from audits.views.prompt import load_system_prompt
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def template_content():
    return (
        "# Agent Description\n\n"
        "You are an expert assistant.\n\n"
        "## Criterion to analyze\n\n"
        "{criterion_name}\n"
        "Detailed description: {criterion_description}.\n\n"
        "## Language used\n\n"
        "Respond in {language}.\n\n"
        "## Resources\n\n"
        "{resources}\n"
    )


class TestLoadSystemPrompt:
    """Unit tests for the load_system_prompt function."""

    def test_load_system_prompt_replaces_all_placeholders(self, template_content):
        """Test that all placeholders are correctly replaced."""

        with patch("builtins.open", mock_open(read_data=template_content)):

            result = load_system_prompt(
                criterion_name="Test Criterion",
                criterion_description="This is a test description",
                resources="- Resource 1: http://example.com\n- Resource 2: http://test.com",
                language="french",
            )

            assert result == (
                "# Agent Description\n\n"
                "You are an expert assistant.\n\n"
                "## Criterion to analyze\n\n"
                "Test Criterion\n"
                "Detailed description: This is a test description.\n\n"
                "## Language used\n\n"
                "Respond in french.\n\n"
                "## Resources\n\n"
                "- Resource 1: http://example.com\n"
                "- Resource 2: http://test.com\n"
            )

    def test_load_system_prompt_with_empty_strings(self, template_content):
        """Test that the function works with empty strings."""

        with patch("builtins.open", mock_open(read_data=template_content)):

            result = load_system_prompt(
                criterion_name="",
                criterion_description="",
                resources="",
                language="",
            )

            assert result == (
                "# Agent Description\n\n"
                "You are an expert assistant.\n\n"
                "## Criterion to analyze\n\n"
                "\n"
                "Detailed description: .\n\n"
                "## Language used\n\n"
                "Respond in .\n\n"
                "## Resources\n\n"
                "\n"
            )

    def test_load_system_prompt_with_special_characters(self, template_content):
        """Test that the function handles special characters correctly."""

        with patch("builtins.open", mock_open(read_data=template_content)):

            result = load_system_prompt(
                criterion_name="Criterion & Test < > \" '",
                criterion_description="Description with\nnewlines\tand\ttabs",
                resources="Resource: https://example.com?param=value&other=test",
                language="français",
            )

            assert result == (
                "# Agent Description\n\n"
                "You are an expert assistant.\n\n"
                "## Criterion to analyze\n\n"
                "Criterion & Test < > \" '\n"
                "Detailed description: Description with\nnewlines\tand\ttabs.\n\n"
                "## Language used\n\n"
                "Respond in français.\n\n"
                "## Resources\n\n"
                "Resource: https://example.com?param=value&other=test\n"
            )

    def test_load_system_prompt_uses_correct_file_path(self, template_content):
        """Test that the correct file path is used."""

        with patch("builtins.open", mock_open(read_data=template_content)) as mock_file:
            load_system_prompt(
                criterion_name="Test",
                criterion_description="Test",
                resources="Test",
                language="english",
            )

            # Check that the file is opened with the correct path
            mock_file.assert_called_once()
            call_args = mock_file.call_args
            # The first argument is the file path
            file_path = call_args[0][0]
            assert str(file_path).endswith("audits/prompts/system_prompt.md")

    def test_load_system_prompt_encoding_utf8(self, template_content):
        """Test that the file is read with UTF-8 encoding."""
        with patch("builtins.open", mock_open(read_data=template_content)) as mock_file:
            load_system_prompt(
                criterion_name="Criterion with accents éàù",
                criterion_description="",
                resources="",
                language="french",
            )

            # Vérifier que le fichier est ouvert avec encoding='utf-8'
            mock_file.assert_called_once()
            call_kwargs = mock_file.call_args[1]
            assert call_kwargs.get("encoding") == "utf-8"


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
class TestPromptFormView:
    """Test the prompt form view."""

    def test_login_required(self, client, project_audit_criterion):
        response = client.get(
            reverse(
                "audits:prompt",
                kwargs={
                    "project_slug": project_audit_criterion.project_audit.project.slug,
                    "audit_id": project_audit_criterion.project_audit.id,
                    "criterion_id": project_audit_criterion.id,
                },
            )
        )
        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_prompt_form_view_get_context(
        self, client, login_user, project_audit_criterion
    ):
        url = reverse(
            "audits:prompt",
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
        assert "session_id" in response.context
        assert isinstance(response.context["session_id"], uuid.UUID)

    def test_prompt_form_view_get_with_valid_session_id(
        self, client, login_user, project_audit_criterion
    ):
        session_id = uuid.uuid4()
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion, session_id=session_id
        )

        url = reverse(
            "audits:prompt",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )
        response = client.get(url, {"session_id": str(session_id)})

        assert response.status_code == 200
        assert response.context["session_id"] == session_id
        assert response.context["prompt"] == prompt

    def test_prompt_form_view_get_with_invalid_session_id(
        self, client, login_user, project_audit_criterion
    ):
        url = reverse(
            "audits:prompt",
            kwargs={
                "project_slug": project_audit_criterion.project_audit.project.slug,
                "audit_id": project_audit_criterion.project_audit.id,
                "criterion_id": project_audit_criterion.id,
            },
        )
        response = client.get(url, {"session_id": "invalid-uuid"})

        assert response.status_code == 200
        assert isinstance(response.context["session_id"], uuid.UUID)
        assert "prompt" not in response.context
