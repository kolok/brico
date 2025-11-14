from audits.models import AuditLibrary, Criterion, Organization, Tag
from django.contrib import admin
from django.utils.text import slugify
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin


class CriterionResource(resources.ModelResource):
    tags = fields.Field(column_name="tags", readonly=False, attribute=None)
    audit_library = fields.Field(column_name="audit_library", attribute="audit_library")

    def dehydrate_audit_library(self, criteria):
        """Export the audit library slug"""
        return criteria.audit_library.slug if criteria.audit_library else ""

    def dehydrate_tags(self, criteria):
        """Dehydrate the tags field"""
        return ", ".join([tag.name for tag in criteria.tags.all()])

    def before_import_row(self, row, **kwargs):
        """Manage the audit library while importing"""
        if "audit_library" in row and row["audit_library"]:
            slug = slugify(row["audit_library"])
            row["audit_library"] = AuditLibrary.objects.get(slug=slug)

    def after_save_instance(self, instance, row, **kwargs):
        if "tags" in row and row["tags"]:
            tags = row["tags"].split(",")
            tags_names = [tag.strip() for tag in tags]
            instance.tags.clear()
            for tag_name in tags_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)

    def get_queryset(self):
        return super().get_queryset().prefetch_related("tags", "audit_library")

    class Meta:
        model = Criterion
        exclude = [
            "created_at",
            "updated_at",
        ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(AuditLibrary)
class AuditLibraryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "organization")
    search_fields = ("name", "slug", "organization__name")
    list_filter = ("organization",)


@admin.register(Criterion)
class CriterionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CriterionResource
    list_display = ("name", "slug", "audit_library")
    search_fields = ("name", "slug", "audit_library__name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("criteria",)
