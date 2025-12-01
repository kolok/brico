import pytest
from audits.models.audit import (
    AuditLibrary,
    Criterion,
    ProjectAudit,
    ProjectAuditCriterion,
    ProjectAuditCriterionComment,
    ProjectAuditCriterionPrompt,
    Tag,
)
from audits.tests.factories import (
    AuditLibraryFactory,
    CriterionFactory,
    ProjectAuditCriterionCommentFactory,
    ProjectAuditCriterionFactory,
    ProjectAuditCriterionPromptFactory,
    ProjectAuditFactory,
    TagFactory,
    UserFactory,
)
from django.db import IntegrityError
from organization.models.organization import Organization
from organization.tests.factories import OrganizationFactory, ProjectFactory


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


@pytest.fixture
def project(organization):
    return ProjectFactory(organization=organization)


@pytest.fixture
def project_audit(project, audit_library):
    return ProjectAuditFactory(project=project, audit_library=audit_library)


@pytest.mark.django_db
class TestProjectAudit:

    def test_project_foreign_key(self, project, audit_library):
        project_audit = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )

        assert project_audit.project == project
        assert project_audit in project.audits.all()

    def test_audit_library_foreign_key(self, project, audit_library):
        project_audit = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )

        assert project_audit.audit_library == audit_library
        assert project_audit in audit_library.projects.all()

    def test_cascade_delete_project(self, project, audit_library):
        project_audit = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )
        project_audit_id = project_audit.id

        project.delete()

        assert not ProjectAudit.objects.filter(id=project_audit_id).exists()

    def test_cascade_delete_audit_library(self, project, audit_library):
        project_audit = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )
        project_audit_id = project_audit.id

        audit_library.delete()

        assert not ProjectAudit.objects.filter(id=project_audit_id).exists()

    def test_project_audits_relation(self, project, audit_library):
        project_audit1 = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )
        audit_library2 = AuditLibraryFactory(organization=project.organization)
        project_audit2 = ProjectAuditFactory(
            project=project, audit_library=audit_library2
        )

        assert project_audit1 in project.audits.all()
        assert project_audit2 in project.audits.all()
        assert project.audits.count() == 2

    def test_audit_library_projects_relation(self, project, audit_library):
        project1 = ProjectFactory(organization=project.organization)
        project_audit1 = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )
        project_audit2 = ProjectAuditFactory(
            project=project1, audit_library=audit_library
        )

        assert project_audit1 in audit_library.projects.all()
        assert project_audit2 in audit_library.projects.all()
        assert audit_library.projects.count() == 2


@pytest.fixture
def project_audit_criterion(project_audit, criterion):
    return ProjectAuditCriterionFactory(
        project_audit=project_audit, criterion=criterion
    )


@pytest.mark.django_db
class TestProjectAuditCriterion:

    def test_project_audit_foreign_key(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion
        )

        assert project_audit_criterion.project_audit == project_audit
        assert project_audit_criterion in project_audit.project_audit_criteria.all()

    def test_criterion_foreign_key(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion
        )

        assert project_audit_criterion.criterion == criterion
        assert project_audit_criterion in criterion.project_audit_criteria.all()

    def test_status_default_value(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion
        )

        assert (
            project_audit_criterion.status
            == ProjectAuditCriterion.ProjectAuditCriterionStatus.NOT_HANDLED_YET
        )

    def test_status_choices(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit,
            criterion=criterion,
            status=ProjectAuditCriterion.ProjectAuditCriterionStatus.COMPLIANT,
        )

        assert (
            project_audit_criterion.status
            == ProjectAuditCriterion.ProjectAuditCriterionStatus.COMPLIANT
        )

        project_audit_criterion.status = (
            ProjectAuditCriterion.ProjectAuditCriterionStatus.NOT_COMPLIANT
        )
        project_audit_criterion.save()

        assert (
            project_audit_criterion.status
            == ProjectAuditCriterion.ProjectAuditCriterionStatus.NOT_COMPLIANT
        )

    def test_cascade_delete_project_audit(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion
        )
        project_audit_criterion_id = project_audit_criterion.id

        project_audit.delete()

        assert not ProjectAuditCriterion.objects.filter(
            id=project_audit_criterion_id
        ).exists()

    def test_cascade_delete_criterion(self, project_audit, criterion):
        project_audit_criterion = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion
        )
        project_audit_criterion_id = project_audit_criterion.id

        criterion.delete()

        assert not ProjectAuditCriterion.objects.filter(
            id=project_audit_criterion_id
        ).exists()

    def test_project_audit_criteria_relation(self, project_audit, audit_library):
        criterion1 = CriterionFactory(
            audit_library=audit_library, public_id="CRI-001", name="Criterion 1"
        )
        criterion2 = CriterionFactory(
            audit_library=audit_library, public_id="CRI-002", name="Criterion 2"
        )
        project_audit_criterion1 = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion1
        )
        project_audit_criterion2 = ProjectAuditCriterionFactory(
            project_audit=project_audit, criterion=criterion2
        )

        assert project_audit_criterion1 in project_audit.project_audit_criteria.all()
        assert project_audit_criterion2 in project_audit.project_audit_criteria.all()
        assert project_audit.project_audit_criteria.count() == 2

    def test_criterion_project_audits_relation(self, project, audit_library, criterion):
        project1 = ProjectFactory(organization=project.organization)
        project_audit1 = ProjectAuditFactory(
            project=project, audit_library=audit_library
        )
        project_audit2 = ProjectAuditFactory(
            project=project1, audit_library=audit_library
        )
        project_audit_criterion1 = ProjectAuditCriterionFactory(
            project_audit=project_audit1, criterion=criterion
        )
        project_audit_criterion2 = ProjectAuditCriterionFactory(
            project_audit=project_audit2, criterion=criterion
        )

        assert project_audit_criterion1 in criterion.project_audit_criteria.all()
        assert project_audit_criterion2 in criterion.project_audit_criteria.all()
        assert criterion.project_audit_criteria.count() == 2


@pytest.mark.django_db
class TestProjectAuditCriterionComment:

    def test_user_foreign_key(self, project_audit_criterion):
        user = UserFactory()
        comment = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion
        )

        assert comment.user == user
        assert comment in user.project_audit_criterion_comments.all()

    def test_project_audit_criterion_foreign_key(self, project_audit_criterion):
        user = UserFactory()
        comment = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion
        )

        assert comment.project_audit_criterion == project_audit_criterion
        assert comment in project_audit_criterion.comments.all()

    def test_comment_default_empty(self, project_audit_criterion):
        user = UserFactory()
        comment = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion, comment=""
        )

        assert comment.comment == ""

    def test_comment_text(self, project_audit_criterion):
        user = UserFactory()
        comment_text = "This is a test comment"
        comment = ProjectAuditCriterionCommentFactory(
            user=user,
            project_audit_criterion=project_audit_criterion,
            comment=comment_text,
        )

        assert comment.comment == comment_text

    def test_cascade_delete_user(self, project_audit_criterion):
        user = UserFactory()
        comment = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion
        )
        comment_id = comment.id

        user.delete()

        assert not ProjectAuditCriterionComment.objects.filter(id=comment_id).exists()

    def test_cascade_delete_project_audit_criterion(self, project_audit_criterion):
        user = UserFactory()
        comment = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion
        )
        comment_id = comment.id

        project_audit_criterion.delete()

        assert not ProjectAuditCriterionComment.objects.filter(id=comment_id).exists()

    def test_user_comments_relation(self, project_audit_criterion):
        user = UserFactory()
        comment1 = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion
        )
        criterion2 = CriterionFactory(
            audit_library=project_audit_criterion.project_audit.audit_library,
            public_id="CRI-002",
        )
        project_audit_criterion2 = ProjectAuditCriterionFactory(
            project_audit=project_audit_criterion.project_audit, criterion=criterion2
        )
        comment2 = ProjectAuditCriterionCommentFactory(
            user=user, project_audit_criterion=project_audit_criterion2
        )

        assert comment1 in user.project_audit_criterion_comments.all()
        assert comment2 in user.project_audit_criterion_comments.all()
        assert user.project_audit_criterion_comments.count() == 2

    def test_project_audit_criterion_comments_relation(self, project_audit_criterion):
        user1 = UserFactory()
        user2 = UserFactory()
        comment1 = ProjectAuditCriterionCommentFactory(
            user=user1, project_audit_criterion=project_audit_criterion
        )
        comment2 = ProjectAuditCriterionCommentFactory(
            user=user2, project_audit_criterion=project_audit_criterion
        )

        assert comment1 in project_audit_criterion.comments.all()
        assert comment2 in project_audit_criterion.comments.all()
        assert project_audit_criterion.comments.count() == 2


@pytest.mark.django_db
class TestProjectAuditCriterionPrompt:

    def test_project_audit_criterion_foreign_key(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )

        assert prompt.project_audit_criterion == project_audit_criterion
        assert prompt in project_audit_criterion.prompts.all()

    def test_session_id_generation(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )

        assert prompt.session_id is not None

    def test_session_id_uniqueness(self, project_audit_criterion):
        prompt1 = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )
        prompt2 = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )

        assert prompt1.session_id != prompt2.session_id

    def test_name_default(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion, name="Prompt"
        )

        assert prompt.name == "Prompt"

    def test_prompt_json_default(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )

        assert isinstance(prompt.prompt, dict)

    def test_prompt_json_content(self, project_audit_criterion):
        prompt_data = {"messages": [{"role": "user", "content": "Test"}]}
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion, prompt=prompt_data
        )

        assert prompt.prompt == prompt_data
        assert prompt.prompt["messages"][0]["content"] == "Test"

    def test_cascade_delete_project_audit_criterion(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )
        prompt_id = prompt.id

        project_audit_criterion.delete()

        assert not ProjectAuditCriterionPrompt.objects.filter(id=prompt_id).exists()

    def test_project_audit_criterion_prompts_relation(self, project_audit_criterion):
        prompt1 = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )
        prompt2 = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion
        )

        assert prompt1 in project_audit_criterion.prompts.all()
        assert prompt2 in project_audit_criterion.prompts.all()
        assert project_audit_criterion.prompts.count() == 2

    def test_str_representation(self, project_audit_criterion):
        prompt = ProjectAuditCriterionPromptFactory(
            project_audit_criterion=project_audit_criterion, name="Test Prompt"
        )

        str_repr = str(prompt)
        assert "Test Prompt" in str_repr
        assert prompt.created_at.strftime("%Y-%m-%d") in str_repr
