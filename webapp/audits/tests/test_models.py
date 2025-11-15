import pytest
from audits.models.audit import AuditLibrary, Criterion, Tag
from audits.tests.factories import AuditLibraryFactory, CriterionFactory, TagFactory
from django.db import IntegrityError
from organization.models.organization import Organization
from organization.tests.factories import OrganizationFactory


@pytest.fixture
def organization():
    return OrganizationFactory()


@pytest.mark.django_db
class TestAuditLibrary:

    def test_slug_generation_automatic(self, organization):
        library = AuditLibraryFactory(name="Audit Library", organization=organization)

        assert library.slug == "audit-library"

    def test_organization_foreign_key(self, organization):
        library = AuditLibraryFactory(organization=organization)

        assert library.organization == organization
        assert library in organization.audit_libraries.all()

    def test_cascade_delete(self, organization):
        library = AuditLibraryFactory(organization=organization)
        library_id = library.id

        organization.delete()

        assert not AuditLibrary.objects.filter(id=library_id).exists()

    def test_unique_together_organization_name(self):
        org1 = OrganizationFactory(name="Organization 1")
        org2 = OrganizationFactory(name="Organization 2")

        lib1 = AuditLibraryFactory(name="Library", organization=org1)
        lib2 = AuditLibraryFactory(name="Library", organization=org2)
        assert lib1.name == lib2.name, "Same name in different organizations"

        with pytest.raises(IntegrityError):
            AuditLibraryFactory(name="Library", organization=org1)

    def test_unique_together_organization_slug(self):
        org1 = OrganizationFactory(name="Organization 1")
        org2 = OrganizationFactory(name="Organization 2")

        lib1 = AuditLibraryFactory(name="Library", organization=org1)
        lib2 = AuditLibraryFactory(name="Library", organization=org2)
        assert lib1.slug == lib2.slug, "Same slug in different organizations"

        with pytest.raises(IntegrityError):
            AuditLibraryFactory(name="Library", organization=org1)

    def test_unique_together_both_constraints(self):
        org1 = OrganizationFactory(name="Organization 1")
        org2 = OrganizationFactory(name="Organization 2")

        lib1 = AuditLibraryFactory(name="My Library", organization=org1)
        original_slug = lib1.slug

        lib2 = AuditLibraryFactory(name="Another Library", organization=org1)
        assert lib2.slug != original_slug

        lib3 = AuditLibraryFactory(name="My Library", organization=org2)
        assert lib3.name == lib1.name, "Same name in different organizations"
        assert lib3.slug == lib1.slug, "Same slug in different organizations"

        with pytest.raises(IntegrityError):
            AuditLibraryFactory(name="My Library", organization=org1)

    def test_str_representation(self, organization):
        library = AuditLibraryFactory(name="Library", organization=organization)
        assert str(library) == "Library"

    def test_organization_audit_libraries_relation(self, organization):
        library1 = AuditLibraryFactory(name="Library 1", organization=organization)
        library2 = AuditLibraryFactory(name="Library 2", organization=organization)

        assert library1 in organization.audit_libraries.all()
        assert library2 in organization.audit_libraries.all()
        assert organization.audit_libraries.count() == 2


@pytest.fixture
def audit_library(organization):
    return AuditLibraryFactory(organization=organization)


@pytest.mark.django_db
class TestCriterion:

    def test_audit_library_foreign_key(self, audit_library):
        criterion = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Criterion",
        )
        assert criterion.audit_library == audit_library
        assert criterion in audit_library.criterias.all()

    def test_cascade_delete(self, audit_library):
        criterion = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
        )
        criterion_id = criterion.id
        audit_library.delete()
        assert not Criterion.objects.filter(id=criterion_id).exists()

    def test_unique_together_audit_library_public_id(self, organization):
        library1 = AuditLibraryFactory(name="Library 1", organization=organization)
        library2 = AuditLibraryFactory(name="Library 2", organization=organization)
        criterion1 = CriterionFactory(
            audit_library=library1,
            public_id="CRI-001",
            name="Criterion 1",
        )
        criterion2 = CriterionFactory(
            audit_library=library2,
            public_id="CRI-001",
            name="Criterion 2",
        )

        assert (
            criterion1.public_id == criterion2.public_id
        ), "Same public_id in different audit libraries"

        with pytest.raises(IntegrityError):
            # Can't create same public_id in the same audit library
            CriterionFactory(
                audit_library=library1,
                public_id="CRI-001",
                name="Criterion 3",
            )

    def test_str_representation(self, audit_library):
        criterion = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Criterion",
        )
        assert str(criterion) == "Criterion"

    def test_audit_library_criterias_relation(self, audit_library):
        criterion1 = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Criterion 1",
        )
        criterion2 = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-002",
            name="Criterion 2",
        )

        assert criterion1 in audit_library.criterias.all()
        assert criterion2 in audit_library.criterias.all()
        assert audit_library.criterias.count() == 2

    def test_cascade_delete_full_hierarchy(self, organization, audit_library):
        criterion = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
        )
        tag = TagFactory(name="Tag Test")
        criterion.tags.add(tag)

        organization.delete()
        assert not Organization.objects.filter(id=organization.id).exists()
        assert not AuditLibrary.objects.filter(id=audit_library.id).exists()
        assert not Criterion.objects.filter(id=criterion.id).exists()
        assert Tag.objects.filter(id=tag.id).exists()


@pytest.fixture
def criterion(audit_library):
    return CriterionFactory(audit_library=audit_library, public_id="CRI-001")


@pytest.mark.django_db
class TestTag:

    def test_name_uniqueness(self):
        TagFactory(name="Tag Unique")
        with pytest.raises(IntegrityError):
            TagFactory(name="Tag Unique")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            TagFactory(name=None)

    def test_many_to_many_relationship(self, audit_library):
        criterion1 = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Criterion 1",
        )
        criterion2 = CriterionFactory(
            audit_library=audit_library,
            public_id="CRI-002",
            name="Criterion 2",
        )
        tag = TagFactory(name="Tag Test")

        tag.criteria.add(criterion1, criterion2)
        assert criterion1 in tag.criteria.all()
        assert criterion2 in tag.criteria.all()

        # Check the reverse relation
        assert tag in criterion1.tags.all()
        assert tag in criterion2.tags.all()

    def test_many_to_many_multiple_tags(self, criterion):
        tag1 = TagFactory(name="Tag 1")
        tag2 = TagFactory(name="Tag 2")

        criterion.tags.add(tag1, tag2)
        assert tag1 in criterion.tags.all()
        assert tag2 in criterion.tags.all()
        assert len(criterion.tags.all()) == 2

    def test_many_to_many_clear(self, criterion):
        tag = TagFactory(name="Tag Test")
        criterion.tags.add(tag)
        assert tag in criterion.tags.all()

        criterion.tags.clear()
        assert tag not in criterion.tags.all()

    def test_str_representation(self):
        tag = TagFactory(name="Tag Test")
        assert str(tag) == "Tag Test"
