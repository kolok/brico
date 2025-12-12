import factory
from django.contrib.auth import get_user_model
from factory import fuzzy
from factory.faker import Faker
from organization.models.organization import (
    Organization,
    OrganizationMember,
    Project,
    Resource,
)

User = get_user_model()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = Faker("company")


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = Faker("user_name")
    email = Faker("email")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "password"  # pragma: allowlist secret
        self.set_password(raw_password)
        if create:
            self.save(update_fields=["password"])


class OrganizationMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationMember

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    is_default = False


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
