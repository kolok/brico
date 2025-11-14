## Test views for the audits app

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home(client):
    response = client.get(reverse("index"))
    assert response.status_code == 200
