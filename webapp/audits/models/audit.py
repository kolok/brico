from audits.models.chat import User
from core.models.mixin import TimestampedModel
from django.db import models
from django_extensions.db.fields import AutoSlugField
from organization.models.organization import Organization, Project


class AuditLibrary(TimestampedModel, models.Model):

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audit_libraries"
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)

    class Meta:
        verbose_name_plural = "Audit Libraries"
        unique_together = [("organization", "name"), ("organization", "slug")]

    def __str__(self):
        return self.name


class Criterion(TimestampedModel, models.Model):

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
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    criteria = models.ManyToManyField(Criterion, related_name="tags", blank=True)

    def __str__(self):
        return self.name


class ProjectAudit(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="audits"
    )
    audit_library = models.ForeignKey(
        AuditLibrary, on_delete=models.CASCADE, related_name="projects"
    )


class ProjectAuditCriterion(TimestampedModel, models.Model):
    class ProjectAuditCriterionStatus(models.TextChoices):
        NOT_HANDLED_YET = "NOT_HANDLED_YET", "Not Handled Yet"
        NOT_COMPLIANT = "NOT_COMPLIANT", "Not Compliant"
        PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT", "Partially Compliant"
        COMPLIANT = "COMPLIANT", "Compliant"

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
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_audit_criterion_comments"
    )
    project_audit_criterion = models.ForeignKey(
        ProjectAuditCriterion, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField(blank=True, default="", null=False)


class ProjectAuditCriterionPrompt(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    project_audit_criterion = models.ForeignKey(
        ProjectAuditCriterion, on_delete=models.CASCADE, related_name="prompts"
    )
    prompt = models.JSONField(blank=True, default=dict, null=False)
