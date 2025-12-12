import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from organization.admin.organization import (
    OrganizationAdmin,
    OrganizationMemberInline,
    ProjectAdmin,
    ResourceAdmin,
    UserAdmin,
    UserOrganizationMemberInline,
)
from organization.models import Organization, OrganizationMember, Project, Resource

User = get_user_model()


@pytest.mark.django_db
class TestOrganizationAdmin:
    def test_organization_admin_is_registered(self):
        """Test that OrganizationAdmin is registered."""
        assert Organization in site._registry
        assert isinstance(site._registry[Organization], OrganizationAdmin)

    def test_organization_admin_has_inlines(self):
        """Test that OrganizationAdmin has the correct inlines."""
        admin_instance = site._registry[Organization]
        assert OrganizationMemberInline in admin_instance.inlines

    def test_organization_admin_list_display(self):
        """Test that OrganizationAdmin has correct list_display."""
        admin_instance = site._registry[Organization]
        assert "name" in admin_instance.list_display
        assert "slug" in admin_instance.list_display

    def test_organization_admin_search_fields(self):
        """Test that OrganizationAdmin has correct search_fields."""
        admin_instance = site._registry[Organization]
        assert "name" in admin_instance.search_fields
        assert "slug" in admin_instance.search_fields

    def test_organization_admin_readonly_fields(self):
        """Test that OrganizationAdmin has correct readonly_fields."""
        admin_instance = site._registry[Organization]
        assert "slug" in admin_instance.readonly_fields
        assert "created_at" in admin_instance.readonly_fields
        assert "updated_at" in admin_instance.readonly_fields


@pytest.mark.django_db
class TestProjectAdmin:
    def test_project_admin_is_registered(self):
        """Test that ProjectAdmin is registered."""
        assert Project in site._registry
        assert isinstance(site._registry[Project], ProjectAdmin)

    def test_project_admin_list_display(self):
        """Test that ProjectAdmin has correct list_display."""
        admin_instance = site._registry[Project]
        assert "name" in admin_instance.list_display
        assert "slug" in admin_instance.list_display
        assert "organization" in admin_instance.list_display

    def test_project_admin_search_fields(self):
        """Test that ProjectAdmin has correct search_fields."""
        admin_instance = site._registry[Project]
        assert "name" in admin_instance.search_fields
        assert "slug" in admin_instance.search_fields
        assert "organization__name" in admin_instance.search_fields

    def test_project_admin_readonly_fields(self):
        """Test that ProjectAdmin has correct readonly_fields."""
        admin_instance = site._registry[Project]
        assert "slug" in admin_instance.readonly_fields
        assert "created_at" in admin_instance.readonly_fields
        assert "updated_at" in admin_instance.readonly_fields


@pytest.mark.django_db
class TestResourceAdmin:
    def test_resource_admin_is_registered(self):
        """Test that ResourceAdmin is registered."""
        assert Resource in site._registry
        assert isinstance(site._registry[Resource], ResourceAdmin)

    def test_resource_admin_list_display(self):
        """Test that ResourceAdmin has correct list_display."""
        admin_instance = site._registry[Resource]
        assert "name" in admin_instance.list_display
        assert "type" in admin_instance.list_display
        assert "project" in admin_instance.list_display
        assert "project__organization" in admin_instance.list_display

    def test_resource_admin_search_fields(self):
        """Test that ResourceAdmin has correct search_fields."""
        admin_instance = site._registry[Resource]
        assert "name" in admin_instance.search_fields
        assert "type" in admin_instance.search_fields
        assert "project__name" in admin_instance.search_fields
        assert "project__organization__name" in admin_instance.search_fields

    def test_resource_admin_readonly_fields(self):
        """Test that ResourceAdmin has correct readonly_fields."""
        admin_instance = site._registry[Resource]
        assert "created_at" in admin_instance.readonly_fields
        assert "updated_at" in admin_instance.readonly_fields


@pytest.mark.django_db
class TestUserAdmin:
    def test_user_admin_is_registered(self):
        """Test that UserAdmin is registered."""
        assert User in site._registry
        assert isinstance(site._registry[User], UserAdmin)

    def test_user_admin_has_inlines(self):
        """Test that UserAdmin has the correct inlines."""
        admin_instance = site._registry[User]
        assert UserOrganizationMemberInline in admin_instance.inlines


@pytest.mark.django_db
class TestOrganizationMemberInline:
    def test_inline_model(self):
        """Test that OrganizationMemberInline uses the correct model."""
        assert OrganizationMemberInline.model == OrganizationMember

    def test_inline_fk_name(self):
        """Test that OrganizationMemberInline has correct fk_name."""
        assert OrganizationMemberInline.fk_name == "organization"

    def test_inline_extra(self):
        """Test that OrganizationMemberInline has correct extra."""
        assert OrganizationMemberInline.extra == 0


@pytest.mark.django_db
class TestUserOrganizationMemberInline:
    def test_inline_model(self):
        """Test that UserOrganizationMemberInline uses the correct model."""
        assert UserOrganizationMemberInline.model == OrganizationMember

    def test_inline_fk_name(self):
        """Test that UserOrganizationMemberInline has correct fk_name."""
        assert UserOrganizationMemberInline.fk_name == "user"

    def test_inline_extra(self):
        """Test that UserOrganizationMemberInline has correct extra."""
        assert UserOrganizationMemberInline.extra == 0
