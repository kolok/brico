import factory
from audits.models.audit import (
    AuditLibrary,
    Criterion,
    ProjectAudit,
    ProjectAuditCriterion,
    ProjectAuditCriterionComment,
    ProjectAuditCriterionPrompt,
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

    username = Faker("user_name")
    email = Faker("email")
    password = factory.PostGenerationMethodCall(
        "set_password", "password"
    )  # pragma: allowlist secret


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


class ProjectAuditCriterionCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectAuditCriterionComment

    user = factory.SubFactory(UserFactory)
    project_audit_criterion = factory.SubFactory(ProjectAuditCriterionFactory)
    comment = Faker("text", max_nb_chars=500)


class ProjectAuditCriterionPromptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectAuditCriterionPrompt

    project_audit_criterion = factory.SubFactory(ProjectAuditCriterionFactory)
    name = Faker("sentence", nb_words=3)
    prompt = factory.LazyFunction(lambda: {"messages": []})
