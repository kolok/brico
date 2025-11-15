import pytest
from audits.admin.audit import CriterionResource
from audits.models.audit import AuditLibrary, Criterion, Tag
from organization.models.organization import Organization
from tablib import Dataset


@pytest.fixture
def organization():
    return Organization.objects.create(name="My Organization")


@pytest.fixture
def audit_library(organization):
    return AuditLibrary.objects.create(name="Library", organization=organization)


@pytest.fixture
def criterion(audit_library):
    return Criterion.objects.create(
        audit_library=audit_library, public_id="CRI-001", name="Test Criterion"
    )


@pytest.fixture
def tag():
    return Tag.objects.create(name="Tag 1")


@pytest.mark.django_db
class TestCriterionResource:

    def test_export_criterion_with_tags(self, audit_library, criterion):
        """Test the export of a criterion with its tags."""
        tag1 = Tag.objects.create(name="Tag 1")
        tag2 = Tag.objects.create(name="Tag 2")
        criterion.tags.add(tag1, tag2)

        resource = CriterionResource()
        dataset = resource.export(Criterion.objects.filter(id=criterion.id))

        assert len(dataset) == 1
        exported_row = dataset[0]

        assert exported_row[dataset.headers.index("name")] == "Test Criterion"
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
                "New Criterion",
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
        assert criterion.name == "New Criterion"
        assert criterion.audit_library == audit_library

        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Tag 1" in tag_names
        assert "Tag 2" in tag_names
        assert "Tag 3" in tag_names
        assert len(criterion.tags.all()) == 3

    def test_import_criterion_existing_tags(self, audit_library):
        Tag.objects.create(name="Existing Tag")

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
                "Criterion with Existing Tags",
                "Description",
                audit_library.slug,
                "Existing Tag, New Tag",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        assert not result.has_errors()
        criterion = Criterion.objects.get(public_id="CRI-003")

        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Existing Tag" in tag_names
        assert "New Tag" in tag_names
        assert Tag.objects.filter(name="Existing Tag").count() == 1

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
                "Criterion",
                "Description",
                "slug-inexistant",
                "",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        # The import must fail because the audit_library does not exist
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
                "Modified Criterion",
                "New description",
                audit_library.slug,
                "Tag 1",
            ]
        )

        resource = CriterionResource()
        resource.import_data(dataset, dry_run=False)

        criterion.refresh_from_db()
        assert criterion.name == "Modified Criterion"
        assert criterion.description == "New description"
        assert "Tag 1" in [tag.name for tag in criterion.tags.all()]

    def test_import_criterion_tags_cleared_before_add(self, audit_library, criterion):
        tag1 = Tag.objects.create(name="Old Tag 1")
        tag2 = Tag.objects.create(name="Old Tag 2")
        criterion.tags.add(tag1, tag2)

        # Import with new tags
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
                "Criterion",
                "Description",
                audit_library.slug,
                "New Tag 1, New Tag 2",
            ]
        )

        resource = CriterionResource()
        resource.import_data(dataset, dry_run=False)

        criterion.refresh_from_db()
        tag_names = [tag.name for tag in criterion.tags.all()]
        assert "Old Tag 1" not in tag_names
        assert "Old Tag 2" not in tag_names
        assert "New Tag 1" in tag_names
        assert "New Tag 2" in tag_names

    def test_export_excludes_timestamps(self, criterion):

        resource = CriterionResource()
        dataset = resource.export(Criterion.objects.filter(id=criterion.id))

        # Check that created_at and updated_at are not in the headers
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
                "Criterion Without Tags",
                "Description",
                audit_library.slug,
                "",
            ]
        )

        resource = CriterionResource()
        result = resource.import_data(dataset, dry_run=False)

        assert not result.has_errors()
        assert criterion.tags.count() == 0
