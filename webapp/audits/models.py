# Create your models here.
from django.db import models
from django_extensions.db.fields import AutoSlugField


class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    slug = AutoSlugField(populate_from="name", unique=True)  # type: ignore
    description = models.TextField(blank=True, default="", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AuditLibrary(models.Model):

    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audit_libraries"
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Audit Libraries"
        unique_together = ("organization", "slug")

    def __str__(self):
        return self.name


class Criterion(models.Model):

    id = models.AutoField(primary_key=True)
    audit_library = models.ForeignKey(
        AuditLibrary, on_delete=models.CASCADE, related_name="criterias"
    )
    public_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(blank=True, default="", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Criteria"
        unique_together = ("audit_library", "public_id")

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    criteria = models.ManyToManyField(Criterion, related_name="tags", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
