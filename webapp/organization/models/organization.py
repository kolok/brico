from core.models.mixin import TimestampedModel
from django.db import models
from django_extensions.db.fields import AutoSlugField


class Organization(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    slug = AutoSlugField(populate_from="name", unique=True)  # type: ignore
    description = models.TextField(blank=True, default="", null=False)

    def __str__(self):
        return self.name


class Project(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)

    def __str__(self):
        return self.name


class Resource(TimestampedModel, models.Model):
    class ResourceType(models.TextChoices):
        FRONTEND_CODE = "frontend_code"
        BACKEND_CODE = "backend_code"
        INFRASTRUCTURE = "infrastructure"
        TECHNICAL_DOCUMENTATION = "technical_documentation"
        BUSINESS_DOCUMENTATION = "business_documentation"

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="resources"
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=ResourceType.choices, null=True)
    url = models.URLField(blank=True, default="", null=True)
    description = models.TextField(blank=True, default="", null=False)

    def __str__(self):
        return self.name
