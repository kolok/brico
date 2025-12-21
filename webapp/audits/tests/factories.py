import factory
from audits.models.audit import (
    AuditLibrary,
    Comment,
    Criterion,
    ProjectAudit,
    ProjectAuditCriterion,
    Prompt,
    Tag,
)
from django.contrib.auth.models import User
from factory.declarations import Sequence
from factory.faker import Faker
from organization.tests.factories import OrganizationFactory, ProjectFactory


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


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        # factory_boy is deprecating the implicit save-after-post_generation behavior.
        # We opt out of the automatic save and save explicitly in our post_generation
        # hook to keep password persistence stable across versions.
        skip_postgeneration_save = True

    username = Faker("user_name")
    email = Faker("email")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "password"  # pragma: allowlist secret
        self.set_password(raw_password)
        if create:
            self.save(update_fields=["password"])


class ProjectAuditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectAudit

    project = factory.SubFactory(ProjectFactory)
    audit_library = factory.SubFactory(AuditLibraryFactory)


class ProjectAuditCriterionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectAuditCriterion

    project_audit = factory.SubFactory(ProjectAuditFactory)
    criterion = factory.SubFactory(CriterionFactory)
    status = ProjectAuditCriterion.ProjectAuditCriterionStatus.NOT_HANDLED_YET


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    user = factory.SubFactory(UserFactory)
    project_audit_criterion = factory.SubFactory(ProjectAuditCriterionFactory)
    comment = Faker("text", max_nb_chars=500)


class PromptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Prompt

    project_audit_criterion = factory.SubFactory(ProjectAuditCriterionFactory)
    name = Faker("sentence", nb_words=3)
    prompt = factory.LazyFunction(lambda: {"messages": []})
