import factory
from factory import fuzzy
from factory.faker import Faker
from organization.models.organization import Organization, Project, Resource


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = Faker("company")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = Faker("catch_phrase")
    organization = factory.SubFactory(OrganizationFactory)


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resource

    name = Faker("sentence", nb_words=3)
    project = factory.SubFactory(ProjectFactory)
    type = fuzzy.FuzzyChoice([choice[0] for choice in Resource.ResourceType.choices])
    url = Faker("url")
    description = Faker("text", max_nb_chars=200)
