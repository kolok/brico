from pathlib import Path
from unittest.mock import mock_open, patch

from audits.views.prompt import load_system_prompt


class TestLoadSystemPrompt:
    """Tests unitaires pour la fonction load_system_prompt."""

    def test_load_system_prompt_replaces_all_placeholders(self):
        """Test que tous les placeholders sont correctement remplacés."""
        template_content = (
            "# Agent Description\n\n"
            "You are an expert assistant.\n\n"
            "## Criterion to analyze\n\n"
            "{criterion_name}\n"
            "Detailed description: {criterion_description}.\n\n"
            "## Language used\n\n"
            "Respond in {language}.\n\n"
            "## Resources\n\n"
            "{ressources}\n"
        )

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                result = load_system_prompt(
                    criterion_name="Test Criterion",
                    criterion_description="This is a test description",
                    ressources="- Resource 1: http://example.com\n- Resource 2: http://test.com",
                    language="french",
                )

                assert "Test Criterion" in result
                assert "This is a test description" in result
                assert "- Resource 1: http://example.com" in result
                assert "- Resource 2: http://test.com" in result
                assert "french" in result
                assert "{criterion_name}" not in result
                assert "{criterion_description}" not in result
                assert "{language}" not in result
                assert "{ressources}" not in result

    def test_load_system_prompt_with_empty_strings(self):
        """Test que la fonction fonctionne avec des chaînes vides."""
        template_content = (
            "Criterion: {criterion_name}\n"
            "Description: {criterion_description}\n"
            "Language: {language}\n"
            "Resources: {ressources}\n"
        )

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                result = load_system_prompt(
                    criterion_name="",
                    criterion_description="",
                    ressources="",
                    language="",
                )

                assert result is not None
                assert "Criterion: \n" in result
                assert "Description: \n" in result
                assert "Language: \n" in result
                assert "Resources: \n" in result

    def test_load_system_prompt_with_special_characters(self):
        """Test que la fonction gère correctement les caractères spéciaux."""
        template_content = (
            "Name: {criterion_name}\n"
            "Description: {criterion_description}\n"
            "Language: {language}\n"
            "Resources: {ressources}\n"
        )

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                result = load_system_prompt(
                    criterion_name="Criterion & Test < > \" '",
                    criterion_description="Description with\nnewlines\tand\ttabs",
                    ressources="Resource: https://example.com?param=value&other=test",
                    language="français",
                )

                assert "Criterion & Test < > \" '" in result
                assert "Description with\nnewlines\tand\ttabs" in result
                assert "https://example.com?param=value&other=test" in result
                assert "français" in result

    def test_load_system_prompt_uses_correct_file_path(self):
        """Test que le bon chemin de fichier est utilisé."""
        template_content = "Test template"

        with patch("builtins.open", mock_open(read_data=template_content)) as mock_file:
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                load_system_prompt(
                    criterion_name="Test",
                    criterion_description="Test",
                    ressources="Test",
                    language="english",
                )

                # Vérifier que le fichier est ouvert avec le bon chemin
                mock_file.assert_called_once()
                call_args = mock_file.call_args
                # Le premier argument est le chemin du fichier
                file_path = call_args[0][0]
                assert str(file_path).endswith("audits/prompts/system_prompt.md")

    def test_load_system_prompt_encoding_utf8(self):
        """Test que le fichier est lu avec l'encodage UTF-8."""
        template_content = "Criterion: {criterion_name}\nLanguage: {language}"

        with patch("builtins.open", mock_open(read_data=template_content)) as mock_file:
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                load_system_prompt(
                    criterion_name="Critère avec accents éàù",
                    criterion_description="",
                    ressources="",
                    language="français",
                )

                # Vérifier que le fichier est ouvert avec encoding='utf-8'
                mock_file.assert_called_once()
                call_kwargs = mock_file.call_args[1]
                assert call_kwargs.get("encoding") == "utf-8"

    def test_load_system_prompt_multiline_resources(self):
        """Test avec des ressources multilignes."""
        template_content = "Resources:\n{ressources}"

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                ressources = (
                    "- Type 1: http://example.com/resource1\n"
                    "- Type 2: http://example.com/resource2\n"
                    "- Type 3: http://example.com/resource3"
                )

                result = load_system_prompt(
                    criterion_name="Test",
                    criterion_description="Test",
                    ressources=ressources,
                    language="english",
                )

                assert "Type 1: http://example.com/resource1" in result
                assert "Type 2: http://example.com/resource2" in result
                assert "Type 3: http://example.com/resource3" in result

    def test_load_system_prompt_preserves_template_structure(self):
        """Test que la structure du template est préservée après remplacement."""
        template_content = (
            "# Header\n\n"
            "Some text before.\n\n"
            "Criterion: {criterion_name}\n\n"
            "More text.\n"
            "Description: {criterion_description}\n"
            "Language: {language}\n"
            "Resources: {ressources}\n\n"
            "Some text after."
        )

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("audits.views.prompt.settings") as mock_settings:
                mock_settings.BASE_DIR = Path("/fake/base/dir")

                result = load_system_prompt(
                    criterion_name="Test Criterion",
                    criterion_description="Test Description",
                    ressources="Test Resources",
                    language="english",
                )

                # Vérifier que la structure est préservée
                assert result.startswith("# Header")
                assert "Some text before." in result
                assert "Some text after." in result
                assert result.count("\n") >= template_content.count("\n")
