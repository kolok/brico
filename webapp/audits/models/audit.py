from uuid import uuid4

from core.models.mixin import TimestampedModel
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import AutoSlugField
from organization.models.organization import Organization, Project


class AuditLibrary(TimestampedModel, models.Model):
    """Library of audit templates available to organizations."""

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audit_libraries"
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)

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

    class Meta:
        verbose_name_plural = "Criteria"
        unique_together = ("audit_library", "public_id")

    def __str__(self):
        return self.name


class Tag(TimestampedModel, models.Model):
    """Tag to categorize audit criteria."""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    criteria = models.ManyToManyField(Criterion, related_name="tags", blank=True)

    def __str__(self):
        return self.name


class ProjectAudit(TimestampedModel, models.Model):
    """Audit instance for a specific project."""

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="audits"
    )
    audit_library = models.ForeignKey(
        AuditLibrary, on_delete=models.CASCADE, related_name="projects"
    )


class ProjectAuditCriterion(TimestampedModel, models.Model):
    """Assessment of a specific criterion for a project audit."""

    class ProjectAuditCriterionStatus(models.TextChoices):
        NOT_HANDLED_YET = "NOT_HANDLED_YET", "⚪️ Not Handled Yet"
        NOT_COMPLIANT = "NOT_COMPLIANT", "🔴 Not Compliant"
        PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT", "🟡 Partially Compliant"
        COMPLIANT = "COMPLIANT", "🟢 Compliant"

    id = models.AutoField(primary_key=True)
    project_audit = models.ForeignKey(
        ProjectAudit, on_delete=models.CASCADE, related_name="criteria"
    )
    criterion = models.ForeignKey(
        Criterion, on_delete=models.CASCADE, related_name="project_audits"
    )
    status = models.CharField(
        max_length=255,
        choices=ProjectAuditCriterionStatus.choices,
        default=ProjectAuditCriterionStatus.NOT_HANDLED_YET,
    )


class ProjectAuditCriterionComment(TimestampedModel, models.Model):
    """User comment on a criterion assessment."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_audit_criterion_comments"
    )
    project_audit_criterion = models.ForeignKey(
        ProjectAuditCriterion, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField(blank=True, default="", null=False)


class ProjectAuditCriterionPrompt(TimestampedModel, models.Model):
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
