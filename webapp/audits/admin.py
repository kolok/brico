# Register your models here.
from django.contrib import admin
from django.utils.text import slugify
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin

from .models import AuditLibrary, Criteria, Organization, Tag


class CriteriaRessource(resources.ModelResource):
    tags = fields.Field(column_name="tags", readonly=False)
    audit_library = fields.Field(column_name="audit_library", attribute="audit_library")

    def dehydrate_audit_library(self, criteria):
        """Exporte le slug de audit_library au lieu de l'ID"""
        return criteria.audit_library.slug if criteria.audit_library else ""

    def dehydrate_tags(self, criteria):
        """Dehydrate the tags field"""
        return ", ".join([tag.name for tag in criteria.tags.all()])

    def before_import_row(self, row, **kwargs):
        """Convertit le slug de audit_library en ID avant l'import"""
        if "audit_library" in row and row["audit_library"]:
            slug = slugify(row["audit_library"])
            row["audit_library"] = AuditLibrary.objects.get(slug=slug)

    def after_save_instance(self, instance, row, **kwargs):
        if "tags" in row and row["tags"]:
            tags = row["tags"].split(",")
            tags_names = [tag.strip() for tag in tags]
            instance.tags.clear()
            for tag_name in tags_names:
                slug = slugify(tag_name.strip())
                tag, created = Tag.objects.get_or_create(slug=slug)
                instance.tags.add(tag)

    def get_queryset(self):
        return super().get_queryset().prefetch_related("tags", "audit_library")

    class Meta:
        model = Criteria
        # import_id_fields = ("public_id", "audit_library")
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
    search_fields = ("name", "slug", "organization")
    list_filter = ("organization",)


# InlineModelAdmin = admin.TabularInline(model=Tags, fields=("name",))


@admin.register(Criteria)
class CriteriaAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CriteriaRessource
    list_display = ("name", "slug", "audit_library")
    search_fields = ("name", "slug", "audit_library")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("criteria",)
