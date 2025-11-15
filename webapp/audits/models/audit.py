from core.models.mixin import TimestampedModel
from django.db import models
from django_extensions.db.fields import AutoSlugField
from organization.models.organization import Organization


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
