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
class TestIndexView:
    """Tests for index view."""

    def test_index_accessible(self, client):
        """Test that index page is accessible (with i18n redirect)."""
        response = client.get("/", follow=True)  # Follow redirects
        assert response.status_code == 200

    def test_index_contains_links(self, client):
        """Test that index page contains navigation links."""
        response = client.get("/", follow=True)  # Follow redirects
        content = response.content.decode("utf-8")
        # Check for either English or Finnish translations
        assert "Profile" in content or "Profiili" in content
        assert "Search" in content or "Hae" in content


@pytest.mark.django_db
class TestProfileView:
    """Tests for profile view."""

    def test_requires_login(self, client):
        """Test that profile requires login."""
        response = client.get(reverse("profile"))
        assert response.status_code == 302  # Redirect to login

    def test_authenticated_user_can_access(self, authenticated_client):
        """Test that authenticated user can access profile."""
        response = authenticated_client.get(reverse("profile"))
        # Will fail OAuth but should reach the view
        assert response.status_code == 200


@pytest.mark.django_db
class TestVueAppView:
    """Tests for Vue.js app view."""

    def test_requires_login(self, client):
        """Test that Vue app requires login."""
        response = client.get(reverse("vue-app"))
        assert response.status_code == 302  # Redirect to login

    def test_authenticated_user_can_access(self, authenticated_client):
        """Test that authenticated user can access Vue app."""
        response = authenticated_client.get(reverse("vue-app"))
        assert response.status_code == 200
        assert b"Vue.js" in response.content


@pytest.mark.django_db
class TestSearchView:
    """Tests for search view."""

    def test_search_page_accessible(self, authenticated_client):
        """Test that search page is accessible."""
        response = authenticated_client.get(reverse("search"))
        assert response.status_code == 200

    def test_search_with_query(self, authenticated_client):
        """Test search with query parameter."""
        response = authenticated_client.get(reverse("search"), {"q": "test"})
        assert response.status_code == 200
