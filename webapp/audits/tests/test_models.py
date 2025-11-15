import pytest
from audits.models.audit import AuditLibrary, Criterion, Tag
from django.db import IntegrityError
from django.utils.text import slugify
from organization.models.organization import Organization


@pytest.fixture
def organization():
    # TODO : use factory-boy
    return Organization.objects.create(name="Mon Organisation")


@pytest.mark.django_db
class TestAuditLibrary:

    def test_slug_generation_automatic(self, organization):
        library = AuditLibrary.objects.create(
            name="Bibliothèque d'Audit", organization=organization
        )

        assert library.slug == "bibliotheque-daudit"

    def test_organization_foreign_key(self, organization):
        library = AuditLibrary.objects.create(
            name="Bibliothèque", organization=organization
        )

        assert library.organization == organization
        assert library in organization.audit_libraries.all()

    def test_cascade_delete(self, organization):
        library = AuditLibrary.objects.create(
            name="Bibliothèque", organization=organization
        )
        library_id = library.id

        organization.delete()

        assert not AuditLibrary.objects.filter(id=library_id).exists()

    def test_unique_together_organization_slug(self):
        org1 = Organization.objects.create(name="Organisation 1")
        org2 = Organization.objects.create(name="Organisation 2")

        lib1 = AuditLibrary.objects.create(name="Bibliothèque", organization=org1)
        lib2 = AuditLibrary.objects.create(name="Bibliothèque", organization=org2)
        assert lib1.slug == lib2.slug, "Same slug in different organizations"

        lib3 = AuditLibrary.objects.create(name="Bibliothèque", organization=org1)
        assert lib3.slug != lib1.slug, "Can't create same slug in the same organization"
        assert lib3.slug.startswith(
            "bibliotheque"
        ), "Slug must start with 'bibliotheque'"

    def test_str_representation(self, organization):
        library = AuditLibrary.objects.create(
            name="Bibliothèque", organization=organization
        )
        assert str(library) == "Bibliothèque"

    def test_organization_audit_libraries_relation(self, organization):
        library1 = AuditLibrary.objects.create(
            name="Bibliothèque 1", organization=organization
        )
        library2 = AuditLibrary.objects.create(
            name="Bibliothèque 2", organization=organization
        )

        assert library1 in organization.audit_libraries.all()
        assert library2 in organization.audit_libraries.all()
        assert organization.audit_libraries.count() == 2


@pytest.fixture
def audit_library(organization):
    return AuditLibrary.objects.create(name="Bibliothèque", organization=organization)


@pytest.mark.django_db
class TestCriterion:

    def test_slug_generation_automatic(self, audit_library):
        criterion = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère de Test",
        )
        assert criterion.slug == slugify("Critère de Test")
        assert criterion.slug == "critere-de-test"

    def test_audit_library_foreign_key(self, audit_library):
        criterion = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère",
        )
        assert criterion.audit_library == audit_library
        assert criterion in audit_library.criterias.all()

    def test_cascade_delete(self, audit_library):
        criterion = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère",
        )
        criterion_id = criterion.id
        audit_library.delete()
        assert not Criterion.objects.filter(id=criterion_id).exists()

    def test_unique_together_audit_library_public_id(self, organization):
        library1 = AuditLibrary.objects.create(
            name="Bibliothèque 1", organization=organization
        )
        library2 = AuditLibrary.objects.create(
            name="Bibliothèque 2", organization=organization
        )
        criterion1 = Criterion.objects.create(
            audit_library=library1,
            public_id="CRI-001",
            name="Critère 1",
        )
        criterion2 = Criterion.objects.create(
            audit_library=library2,
            public_id="CRI-001",
            name="Critère 2",
        )

        assert (
            criterion1.public_id == criterion2.public_id
        ), "Same public_id in different audit libraries"

        with pytest.raises(IntegrityError):
            # Can't create same public_id in the same audit library
            Criterion.objects.create(
                audit_library=library1,
                public_id="CRI-001",
                name="Critère 3",
            )

    def test_str_representation(self, audit_library):
        criterion = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère",
        )
        assert str(criterion) == "Critère"

    def test_audit_library_criterias_relation(self, audit_library):
        criterion1 = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère 1",
        )
        criterion2 = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-002",
            name="Critère 2",
        )

        assert criterion1 in audit_library.criterias.all()
        assert criterion2 in audit_library.criterias.all()
        assert audit_library.criterias.count() == 2

    def test_cascade_delete_full_hierarchy(self, organization, audit_library):
        criterion = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère",
        )
        tag = Tag.objects.create(name="Tag Test")
        criterion.tags.add(tag)

        organization.delete()
        assert not Organization.objects.filter(id=organization.id).exists()
        assert not AuditLibrary.objects.filter(id=audit_library.id).exists()
        assert not Criterion.objects.filter(id=criterion.id).exists()
        assert Tag.objects.filter(id=tag.id).exists()


@pytest.fixture
def criterion(audit_library):
    return Criterion.objects.create(
        audit_library=audit_library,
        public_id="CRI-001",
        name="Critère",
    )


@pytest.mark.django_db
class TestTag:

    def test_name_uniqueness(self):
        Tag.objects.create(name="Tag Unique")
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Tag Unique")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            Tag.objects.create(name=None)

    def test_many_to_many_relationship(self, audit_library):
        criterion1 = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-001",
            name="Critère 1",
        )
        criterion2 = Criterion.objects.create(
            audit_library=audit_library,
            public_id="CRI-002",
            name="Critère 2",
        )
        tag = Tag.objects.create(name="Tag Test")

        tag.criteria.add(criterion1, criterion2)
        assert criterion1 in tag.criteria.all()
        assert criterion2 in tag.criteria.all()

        # Vérifier la relation inverse
        assert tag in criterion1.tags.all()
        assert tag in criterion2.tags.all()

    def test_many_to_many_multiple_tags(self, criterion):
        tag1 = Tag.objects.create(name="Tag 1")
        tag2 = Tag.objects.create(name="Tag 2")

        criterion.tags.add(tag1, tag2)
        assert tag1 in criterion.tags.all()
        assert tag2 in criterion.tags.all()
        assert len(criterion.tags.all()) == 2

    def test_many_to_many_clear(self, criterion):
        tag = Tag.objects.create(name="Tag Test")
        criterion.tags.add(tag)
        assert tag in criterion.tags.all()

        criterion.tags.clear()
        assert tag not in criterion.tags.all()

    def test_str_representation(self):
        tag = Tag.objects.create(name="Tag Test")
        assert str(tag) == "Tag Test"
