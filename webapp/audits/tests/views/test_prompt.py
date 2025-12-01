from unittest.mock import mock_open, patch

import pytest
from audits.views.prompt import load_system_prompt


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

            # Vérifier que le fichier est ouvert avec le bon chemin
            mock_file.assert_called_once()
            call_args = mock_file.call_args
            # Le premier argument est le chemin du fichier
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
