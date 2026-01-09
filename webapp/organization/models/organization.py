from core.models.mixin import TimestampedModel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

User = get_user_model()


class Organization(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255, unique=True, null=False, blank=False, verbose_name=_("Name")
    )
    slug = AutoSlugField(populate_from="name", unique=True)  # type: ignore
    description = models.TextField(
        blank=True, default="", null=False, verbose_name=_("Description")
    )
    members = models.ManyToManyField(
        User,
        through="OrganizationMember",
        related_name="organizations",
    )

    def __str__(self):
        return self.name


class OrganizationMember(TimestampedModel, models.Model):
    """Relationship model for the Many-to-Many User-Organization relationship."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organization_memberships"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="organization_members",
        help_text=_("Role group (administrator, writer, reader)"),
    )
    is_default = models.BooleanField(
        default=False, help_text=_("Default organization for the user")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="unique_default_organization_per_user",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - {self.organization.name} "
            f"({_('default') if self.is_default else ''})"
        )


class Project(TimestampedModel, models.Model):
    id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_("Name")
    )
    slug = AutoSlugField(populate_from="name")  # type: ignore
    description = models.TextField(
        blank=True, default="", null=False, verbose_name=_("Description")
    )

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
