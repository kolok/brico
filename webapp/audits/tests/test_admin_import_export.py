import pytest
from audits.admin import CriterionResource
from audits.models import AuditLibrary, Criterion, Organization, Tag
from tablib import Dataset


@pytest.fixture
def organization():
    return Organization.objects.create(name="Mon Organisation")


@pytest.fixture
def audit_library(organization):
    return AuditLibrary.objects.create(name="Bibliothèque", organization=organization)


@pytest.fixture
def criterion(audit_library):
    return Criterion.objects.create(
        audit_library=audit_library, public_id="CRI-001", name="Critère Test"
    )


@pytest.fixture
def tag():
    return Tag.objects.create(name="Tag 1")


@pytest.mark.django_db
class TestCriterionResource:

    def test_export_criterion_with_tags(self, audit_library, criterion):
        """Test l'export d'un critère avec ses tags."""
        tag1 = Tag.objects.create(name="Tag 1")
        tag2 = Tag.objects.create(name="Tag 2")
        criterion.tags.add(tag1, tag2)

        resource = CriterionResource()
        dataset = resource.export(Criterion.objects.filter(id=criterion.id))

        assert len(dataset) == 1
        exported_row = dataset[0]

        assert exported_row[dataset.headers.index("name")] == "Critère Test"
        assert exported_row[dataset.headers.index("public_id")] == "CRI-001"

        audit_library_index = dataset.headers.index("audit_library")
        assert exported_row[audit_library_index] == audit_library.slug

        tags_index = dataset.headers.index("tags")
        exported_tags = exported_row[tags_index]
        assert "Tag 1" in exported_tags
        assert "Tag 2" in exported_tags

    def test_export_criterion_without_tags(self, criterion):
        resource = CriterionResource()
        dataset = resource.export(Criterion.objects.filter(id=criterion.id))

        assert len(dataset) == 1
        exported_row = dataset[0]
        tags_index = dataset.headers.index("tags")
        assert exported_row[tags_index] == "" or exported_row[tags_index] is None

    def test_import_criterion_with_tags(self, audit_library):
        dataset = Dataset()
        dataset.headers = [
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                "CRI-002",
                "Nouveau Critère",
                "Description",
                audit_library.slug,
                "Tag 1, Tag 2, Tag 3",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        assert not result.has_errors()
        assert result.totals["new"] == 1

        criterion = Criterion.objects.get(public_id="CRI-002")
        assert criterion.name == "Nouveau Critère"
        assert criterion.audit_library == audit_library

        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Tag 1" in tag_names
        assert "Tag 2" in tag_names
        assert "Tag 3" in tag_names
        assert len(criterion.tags.all()) == 3

    def test_import_criterion_existing_tags(self, audit_library):
        Tag.objects.create(name="Tag Existant")

        dataset = Dataset()
        dataset.headers = [
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                "CRI-003",
                "Critère avec Tags Existants",
                "Description",
                audit_library.slug,
                "Tag Existant, Nouveau Tag",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        assert not result.has_errors()
        criterion = Criterion.objects.get(public_id="CRI-003")

        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Tag Existant" in tag_names
        assert "Nouveau Tag" in tag_names
        assert Tag.objects.filter(name="Tag Existant").count() == 1

    @pytest.mark.django_db
    def test_import_criterion_invalid_audit_library(self):
        dataset = Dataset()
        dataset.headers = [
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                "CRI-005",
                "Critère",
                "Description",
                "slug-inexistant",
                "",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        # L'import doit échouer car l'audit_library n'existe pas
        assert result.has_errors() or result.totals["error"] > 0

    def test_import_criterion_update_existing(self, audit_library, criterion):

        dataset = Dataset()
        dataset.headers = [
            "id",
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                criterion.id,
                criterion.public_id,
                "Critère Modifié",
                "Nouvelle description",
                audit_library.slug,
                "Tag 1",
            ]
        )

        resource = CriterionResource()
        resource.import_data(dataset, dry_run=False)

        criterion.refresh_from_db()
        assert criterion.name == "Critère Modifié"
        assert criterion.description == "Nouvelle description"
        assert "Tag 1" in [tag.name for tag in criterion.tags.all()]

    def test_import_criterion_tags_cleared_before_add(self, audit_library, criterion):
        tag1 = Tag.objects.create(name="Ancien Tag 1")
        tag2 = Tag.objects.create(name="Ancien Tag 2")
        criterion.tags.add(tag1, tag2)

        # Importer avec de nouveaux tags
        dataset = Dataset()
        dataset.headers = [
            "id",
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                criterion.id,
                criterion.public_id,
                "Critère",
                "Description",
                audit_library.slug,
                "Nouveau Tag 1, Nouveau Tag 2",
            ]
        )

        resource = CriterionResource()
        resource.import_data(dataset, dry_run=False)

        criterion.refresh_from_db()
        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Ancien Tag 1" not in tag_names
        assert "Ancien Tag 2" not in tag_names
        assert "Nouveau Tag 1" in tag_names
        assert "Nouveau Tag 2" in tag_names

    def test_export_excludes_timestamps(self, criterion):

        resource = CriterionResource()
        dataset = resource.export(Criterion.objects.filter(id=criterion.id))

        # Vérifier que created_at et updated_at ne sont pas dans les headers
        assert "created_at" not in dataset.headers
        assert "updated_at" not in dataset.headers

    def test_import_empty_tags(self, audit_library, criterion):

        dataset = Dataset()
        dataset.headers = [
            "public_id",
            "name",
            "description",
            "audit_library",
            "tags",
        ]
        dataset.append(
            [
                "CRI-009",
                "Critère Sans Tags",
                "Description",
                audit_library.slug,
                "",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        assert not result.has_errors()
        assert criterion.tags.count() == 0
