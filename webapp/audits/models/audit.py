from collections import Counter
from uuid import uuid4

from core.models.mixin import TimestampedModel
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from organization.models.organization import Organization, Project


class Tag(TimestampedModel, models.Model):
    """Tag to categorize audit criteria."""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    slug = AutoSlugField(populate_from="name")  # type: ignore[arg-type]
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class AuditLibrary(TimestampedModel, models.Model):
    """Library of audit templates available to organizations."""

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="audit_libraries",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")  # type: ignore[arg-type]
    description = models.TextField(blank=True, default="", null=False)
    tags = models.ManyToManyField(Tag, related_name="audit_libraries", blank=True)

    class Meta:
        verbose_name_plural = "Audit Libraries"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"], name="unique_organization_name"
            ),
            models.UniqueConstraint(
                fields=["organization", "slug"], name="unique_organization_slug"
            ),
        ]

    def __str__(self):
        return self.name


class Criterion(TimestampedModel, models.Model):
    """Audit criterion definition from an audit library."""

    id = models.AutoField(primary_key=True)
    audit_library = models.ForeignKey(
        AuditLibrary, on_delete=models.CASCADE, related_name="criterias"
    )
    public_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="", null=False)
    tags = models.ManyToManyField(Tag, related_name="criteria", blank=True)

    class Meta:
        verbose_name_plural = "Criteria"
        unique_together = ("audit_library", "public_id")

    def __str__(self):
        return self.name


class ProjectAuditManager(models.Manager):
    """Manager for ProjectAudit model."""

    def get_active(self):
        return self.get_queryset().filter(status=ProjectAudit.ProjectAuditStatus.ACTIVE)

    def get_archived(self):
        return self.get_queryset().filter(
            status=ProjectAudit.ProjectAuditStatus.ARCHIVED
        )


class ProjectAudit(TimestampedModel, models.Model):
    """Audit instance for a specific project."""

    class ProjectAuditStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("🟢 Active")
        ARCHIVED = "ARCHIVED", _(" Archived")

    objects = ProjectAuditManager()

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="audits"
    )
    audit_library = models.ForeignKey(
        AuditLibrary, on_delete=models.CASCADE, related_name="projects"
    )
    status = models.CharField(
        max_length=255,
        choices=ProjectAuditStatus.choices,
        default=ProjectAuditStatus.ACTIVE,
        verbose_name=_("Status"),
    )

    def get_completion_percentage(self) -> float:
        """
        percentage of criteria that have been handled
        (i.e., not in NOT_HANDLED_YET status)
        """
        nb_criteria_by_status = self._nb_criteria_by_status()
        if nb_criteria_by_status["ALL"] == 0:
            return 0
        return round(
            (nb_criteria_by_status["ALL"] - nb_criteria_by_status["NOT_HANDLED_YET"])
            / nb_criteria_by_status["ALL"]
            * 100,
            2,
        )

    def get_compliance_percentage(self) -> dict[str, float]:
        """
        percentage of criteria that are compliant or partially compliant
        among applicable criteria
        """
        nb_criteria_by_status = self._nb_criteria_by_status()
        all_minus_not_applicable = (
            nb_criteria_by_status["ALL"] - nb_criteria_by_status["NOT_APPLICABLE"]
        )
        if all_minus_not_applicable == 0:
            return {
                "completed": 0,
                "partially_completed": 0,
            }
        completed = round(
            nb_criteria_by_status["COMPLIANT"] / all_minus_not_applicable * 100, 2
        )
        partially_completed = round(
            nb_criteria_by_status["PARTIALLY_COMPLIANT"]
            / all_minus_not_applicable
            * 100,
            2,
        )
        return {
            "completed": completed,
            "partially_completed": partially_completed,
        }

    def _nb_criteria_by_status(self) -> dict[str, int]:
        """
        Number of criteria by status
        Use counter to limit the number of queries to DB
        """
        project_audit_criteria = list(self.project_audit_criteria.all())
        counts = Counter(criterion.status for criterion in project_audit_criteria)
        result = {
            "NOT_HANDLED_YET": 0,
            "NOT_COMPLIANT": 0,
            "PARTIALLY_COMPLIANT": 0,
            "COMPLIANT": 0,
            "NOT_APPLICABLE": 0,
            "ALL": counts.total(),
        }
        result.update({key: counts.get(key, 0) for key in counts.keys()})
        return result

    def __str__(self):
        return f"{self.audit_library.name}" + (
            f" ({self.get_status_display()})" if self.status == "ARCHIVED" else ""
        )


class ProjectAuditCriterion(TimestampedModel, models.Model):
    """Assessment of a specific criterion for a project audit."""

    class ProjectAuditCriterionStatus(models.TextChoices):
        NOT_HANDLED_YET = "NOT_HANDLED_YET", _("⚪️ Not Handled Yet")
        NOT_COMPLIANT = "NOT_COMPLIANT", _("🔴 Not Compliant")
        PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT", _("🟡 Partially Compliant")
        COMPLIANT = "COMPLIANT", _("🟢 Compliant")
        NOT_APPLICABLE = "NOT_APPLICABLE", _("❌ Not Applicable")

    id = models.AutoField(primary_key=True)
    project_audit = models.ForeignKey(
        ProjectAudit, on_delete=models.CASCADE, related_name="project_audit_criteria"
    )
    criterion = models.ForeignKey(
        Criterion, on_delete=models.CASCADE, related_name="project_audit_criteria"
    )
    status = models.CharField(
        max_length=255,
        choices=ProjectAuditCriterionStatus.choices,
        default=ProjectAuditCriterionStatus.NOT_HANDLED_YET,
        verbose_name=_("Status"),
    )

    def __str__(self):
        return f"{self.criterion.public_id} - {self.criterion.name}"


class Comment(TimestampedModel, models.Model):
    """User comment on a criterion assessment."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_audit_criterion_comments"
    )
    project_audit_criterion = models.ForeignKey(
        ProjectAuditCriterion, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField(
        blank=True, default="", null=False, verbose_name=_("Comment")
    )


class Prompt(TimestampedModel, models.Model):
    """AI prompt session for criterion assessment assistance."""

    id = models.AutoField(primary_key=True)
    session_id = models.UUIDField(default=uuid4, db_index=True)
    project_audit_criterion = models.ForeignKey(
        ProjectAuditCriterion, on_delete=models.CASCADE, related_name="prompts"
    )
    name = models.CharField(max_length=255, default="Prompt")
    prompt = models.JSONField(blank=True, default=dict, null=False)

    class Meta:
        indexes = [
            models.Index(fields=["project_audit_criterion", "session_id"]),
            models.Index(fields=["project_audit_criterion", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
