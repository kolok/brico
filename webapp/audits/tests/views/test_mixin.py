import pytest
from audits.tests.factories import ProjectAuditCriterionFactory, ProjectAuditFactory
from audits.views.mixin import (
    AuditChildrenMixin,
    CriteriaChildrenMixin,
    ProjectChildrenMixin,
)
from django.contrib.auth import get_user_model
from django.http import Http404
from organization.tests.factories import ProjectFactory

User = get_user_model()


class FakeView(ProjectChildrenMixin):
    """Fake view that uses ProjectChildrenMixin."""

    pass


class FakeAuditView(AuditChildrenMixin):
    """Fake view that uses AuditChildrenMixin."""

    pass


class FakeCriteriaView(CriteriaChildrenMixin):
    """Fake view that uses CriteriaChildrenMixin."""

    pass


@pytest.mark.django_db
class TestProjectChildrenMixin:
    """Test the ProjectChildrenMixin."""

    def test_get_project_returns_correct_project(self):
        project = ProjectFactory()
        view = FakeView()
        view.kwargs = {"project_slug": project.slug}

        result = view._get_project()

        assert result == project
        assert result.slug == project.slug

    def test_get_project_raises_404_for_invalid_slug(self):
        view = FakeView()
        view.kwargs = {"project_slug": "non-existent-slug"}

        with pytest.raises(Http404):
            view._get_project()

    def test_get_project_with_missing_slug(self):
        view = FakeView()
        view.kwargs = {}

        with pytest.raises(Http404):
            view._get_project()


@pytest.mark.django_db
class TestAuditChildrenMixin:
    """Test the AuditChildrenMixin."""

    def test_get_audit_returns_correct_audit(self):
        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)
        view = FakeAuditView()
        view.kwargs = {"project_slug": project.slug, "audit_id": audit.id}

        result = view._get_audit()

        assert result == audit
        assert result.id == audit.id

    def test_get_audit_raises_404_for_invalid_id(self):
        project = ProjectFactory()
        view = FakeAuditView()
        view.kwargs = {"project_slug": project.slug, "audit_id": 99999}

        with pytest.raises(Http404):
            view._get_audit()

    def test_get_audit_with_missing_id(self):
        project = ProjectFactory()
        view = FakeAuditView()
        view.kwargs = {"project_slug": project.slug}

        with pytest.raises(Http404):
            view._get_audit()

    def test_get_project_inherited_from_parent(self):
        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)
        view = FakeAuditView()
        view.kwargs = {"project_slug": project.slug, "audit_id": audit.id}

        # AuditChildrenMixin should inherit _get_project from ProjectChildrenMixin
        result = view._get_project()

        assert result == project


@pytest.mark.django_db
class TestCriteriaChildrenMixin:
    """Test the CriteriaChildrenMixin."""

    def test_get_criterion_returns_correct_criterion(self):
        project_audit_criterion = ProjectAuditCriterionFactory()
        view = FakeCriteriaView()
        view.kwargs = {
            "project_slug": project_audit_criterion.project_audit.project.slug,
            "audit_id": project_audit_criterion.project_audit.id,
            "criterion_id": project_audit_criterion.id,
        }

        result = view._get_criterion()

        assert result == project_audit_criterion
        assert result.id == project_audit_criterion.id

    def test_get_criterion_raises_404_for_invalid_id(self):
        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)
        view = FakeCriteriaView()
        view.kwargs = {
            "project_slug": project.slug,
            "audit_id": audit.id,
            "criterion_id": 99999,
        }

        with pytest.raises(Http404):
            view._get_criterion()

    def test_get_criterion_with_missing_id(self):
        project = ProjectFactory()
        audit = ProjectAuditFactory(project=project)
        view = FakeCriteriaView()
        view.kwargs = {"project_slug": project.slug, "audit_id": audit.id}

        with pytest.raises(Http404):
            view._get_criterion()

    def test_get_audit_inherited_from_parent(self):
        project_audit_criterion = ProjectAuditCriterionFactory()
        view = FakeCriteriaView()
        view.kwargs = {
            "project_slug": project_audit_criterion.project_audit.project.slug,
            "audit_id": project_audit_criterion.project_audit.id,
            "criterion_id": project_audit_criterion.id,
        }

        # CriteriaChildrenMixin should inherit _get_audit from AuditChildrenMixin
        result = view._get_audit()

        assert result == project_audit_criterion.project_audit

    def test_get_project_inherited_from_grandparent(self):
        project_audit_criterion = ProjectAuditCriterionFactory()
        view = FakeCriteriaView()
        view.kwargs = {
            "project_slug": project_audit_criterion.project_audit.project.slug,
            "audit_id": project_audit_criterion.project_audit.id,
            "criterion_id": project_audit_criterion.id,
        }

        # CriteriaChildrenMixin should inherit _get_project from ProjectChildrenMixin
        result = view._get_project()

        assert result == project_audit_criterion.project_audit.project
