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
    name = models.CharField(max_length=255, null=False, blank=False)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)

    class Meta:
        unique_together = [("organization", "name"), ("organization", "slug")]

    def __str__(self):
        return self.name


class Resource(TimestampedModel, models.Model):
    class ResourceType(models.TextChoices):
        FRONTEND_CODE = "frontend_code", "Frontend Code"
        BACKEND_CODE = "backend_code", "Backend Code"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        TECHNICAL_DOCUMENTATION = "technical_documentation", "Technical Documentation"
        BUSINESS_DOCUMENTATION = "business_documentation", "Business Documentation"

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="resources"
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=ResourceType.choices)
    url = models.URLField(blank=True, default="", null=False)
    description = models.TextField(blank=True, default="", null=False)

    def __str__(self):
        return self.name
