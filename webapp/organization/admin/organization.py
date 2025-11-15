from django.contrib import admin
from organization.models.organization import Organization, Project, Resource


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
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
