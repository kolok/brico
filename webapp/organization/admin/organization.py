from django.contrib import admin
from organization.models.organization import Organization, Project, Resource


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    search_fields = ("name", "type")
