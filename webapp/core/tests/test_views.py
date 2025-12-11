import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestIndexView:
    def test_authenticated_user_is_redirected_to_dashboard(self, client):
        User.objects.create_user(
            username="user", password="password"  # pragma: allowlist secret
        )
        client.login(username="user", password="password")  # pragma: allowlist secret

        response = client.get(reverse("index"))

        assert response.status_code == 302
        assert response.url == reverse("dashboard")
