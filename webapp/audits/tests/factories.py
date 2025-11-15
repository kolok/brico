import factory
from audits.models.audit import AuditLibrary, Criterion, Tag
from factory.declarations import Sequence
from factory.faker import Faker
from organization.tests.factories import OrganizationFactory


class AuditLibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLibrary

    name = Faker("catch_phrase")
    organization = factory.SubFactory(OrganizationFactory)


class CriterionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Criterion

    audit_library = factory.SubFactory(AuditLibraryFactory)
    public_id = Sequence(lambda n: f"CRI-{n:03d}")
    name = Faker("sentence", nb_words=4)
    description = Faker("text", max_nb_chars=200)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = Sequence(lambda n: f"Tag {n}")
