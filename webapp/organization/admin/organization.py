from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from organization.models.organization import (
    Organization,
    OrganizationMember,
    Project,
    Resource,
)

User = get_user_model()


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0
    fk_name = "organization"
    verbose_name = "Organization's User"
    verbose_name_plural = "Organization's Users"


class UserOrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0
    fk_name = "user"
    verbose_name = "User's Organization"
    verbose_name_plural = "User's Organizations"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationMemberInline]
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    readonly_fields = ("slug", "created_at", "updated_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization")
    search_fields = ("name", "slug", "organization__name")
    readonly_fields = ("slug", "created_at", "updated_at")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "project", "project__organization")
    search_fields = ("name", "type", "project__name", "project__organization__name")
    readonly_fields = ("created_at", "updated_at")


# Unregister the default User admin if it exists and register a custom one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserOrganizationMemberInline] + list(BaseUserAdmin.inlines)
