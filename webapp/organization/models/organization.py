from core.models.mixin import TimestampedModel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

User = get_user_model()


class Role(models.Model):
    """
    Role model defining organization-scoped permissions.
    Three roles: administrator, writer, reader
    """
    
    class RoleType(models.TextChoices):
        ADMINISTRATOR = "administrator", _("Administrator")
        WRITER = "writer", _("Writer")
        READER = "reader", _("Reader")
    
    name = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        unique=True,
        verbose_name=_("Role name")
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description")
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles",
        verbose_name=_("Permissions")
    )
    
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["name"]
    
    def __str__(self):
        return self.get_name_display()


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
    """Relationship model for the Many-to-Many User-Organization relationship with role."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organization_memberships"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="members",
        verbose_name=_("Role"),
        help_text=_("User's role in this organization")
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
        verbose_name = _("Organization Member")
        verbose_name_plural = _("Organization Members")

    def __str__(self):
        return (
            f"{self.user.username} - {self.organization.name} "
            f"({self.role} - {_('default') if self.is_default else ''})"
        )
    
    def has_permission(self, permission_codename):
        """Check if the user has a specific permission through their role."""
        return self.role.permissions.filter(codename=permission_codename).exists()


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
