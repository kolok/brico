import pytest
from django.db import IntegrityError
from organization.models.organization import Organization


@pytest.mark.django_db
class TestOrganization:
    def test_slug_generation_automatic(self):
        org = Organization.objects.create(name="Organisation & Co. (2024)")

        assert org.slug == "organisation-co-2024"

    def test_name_uniqueness(self):
        Organization.objects.create(name="Organisation Unique")

        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Organisation Unique")

    def test_slug_uniqueness(self):
        org1 = Organization.objects.create(name="Test Organisation")
        org2 = Organization.objects.create(name="Test-Organisation")

        assert org1.slug == "test-organisation"
        assert org2.slug != org1.slug
        assert org2.slug.startswith("test-organisation")

    def test_name_required(self):
        with pytest.raises(IntegrityError):
            Organization.objects.create(name=None)

    def test_str_representation(self):
        org = Organization.objects.create(name="Mon Organisation")

        assert str(org) == "Mon Organisation"
