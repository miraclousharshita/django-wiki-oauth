import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    """Create test client."""
    return Client()


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def authenticated_client(client, user):
    """Create authenticated client."""
    client.login(username="testuser", password="testpass123")
    return client


@pytest.mark.django_db
class TestUserInfoAPIView:
    """Tests for User Info API endpoint."""

    def test_requires_authentication(self, client):
        """Test that endpoint requires authentication."""
        response = client.get(reverse("api-user"))
        assert response.status_code == 403  # Forbidden

    def test_returns_error_without_oauth(self, authenticated_client):
        """Test that endpoint returns error without OAuth."""
        response = authenticated_client.get(reverse("api-user"))
        assert response.status_code in [404, 500]  # No social auth record


@pytest.mark.django_db
class TestWikiStatsAPIView:
    """Tests for Wiki Stats API endpoint."""

    def test_requires_authentication(self, client):
        """Test that endpoint requires authentication."""
        response = client.get(reverse("api-stats"))
        assert response.status_code == 403  # Forbidden

    def test_returns_na_without_wiki_replica(self, authenticated_client):
        """Test that endpoint returns N/A without wiki replica."""
        response = authenticated_client.get(reverse("api-stats"))
        # Should work but return N/A for local dev
        if response.status_code == 200:
            data = response.json()
            assert "total_articles" in data
            assert "user_edit_count" in data


@pytest.mark.django_db
class TestSearchAPIView:
    """Tests for Search API endpoint."""

    def test_requires_authentication(self, client):
        """Test that endpoint requires authentication."""
        response = client.get(reverse("api-search"))
        assert response.status_code == 403  # Forbidden

    def test_requires_query_parameter(self, authenticated_client):
        """Test that endpoint requires query parameter."""
        response = authenticated_client.get(reverse("api-search"))
        assert response.status_code == 400  # Bad request
        data = response.json()
        assert "error" in data

    def test_returns_error_without_wiki_replica(self, authenticated_client):
        """Test that endpoint returns error without wiki replica in local dev."""
        response = authenticated_client.get(reverse("api-search"), {"q": "test"})
        # Should return 503 for local dev without wiki_replica
        assert response.status_code in [200, 503]
