from user_profile.models import WikiActor, WikiPage, WikiRevision


class TestWikiPage:
    """Tests for WikiPage model."""

    def test_full_title_with_underscores(self):
        """Test that full_title replaces underscores with spaces."""
        page = WikiPage(
            page_id=1,
            page_namespace=0,
            page_title="Python_(programming_language)",
            page_is_redirect=False,
            page_is_new=False,
            page_random=0.5,
            page_touched="20231201000000",
            page_latest=1,
            page_len=1000,
        )
        assert page.full_title == "Python (programming language)"

    def test_url_generation(self):
        """Test that URL is generated correctly."""
        page = WikiPage(
            page_id=1,
            page_namespace=0,
            page_title="Python_(programming_language)",
            page_is_redirect=False,
            page_is_new=False,
            page_random=0.5,
            page_touched="20231201000000",
            page_latest=1,
            page_len=1000,
        )
        assert page.url == "https://en.wikipedia.org/wiki/Python_(programming_language)"

    def test_file_namespace_url(self):
        """Test URL generation for File namespace."""
        page = WikiPage(
            page_id=2,
            page_namespace=6,
            page_title="Example.jpg",
            page_is_redirect=False,
            page_is_new=False,
            page_random=0.5,
            page_touched="20231201000000",
            page_latest=1,
            page_len=500,
        )
        assert page.url == "https://en.wikipedia.org/wiki/File:Example.jpg"


class TestWikiRevision:
    """Tests for WikiRevision model."""

    def test_str_representation(self):
        """Test string representation of revision."""
        revision = WikiRevision(
            rev_id=123,
            rev_page=1,
            rev_comment_id=1,
            rev_actor=1,
            rev_timestamp="20231201000000",
            rev_minor_edit=False,
            rev_deleted=0,
            rev_sha1="abc123",
        )
        assert str(revision) == "Revision 123"


class TestWikiActor:
    """Tests for WikiActor model."""

    def test_str_representation(self):
        """Test string representation of actor."""
        actor = WikiActor(actor_id=1, actor_name="TestUser")
        assert str(actor) == "TestUser"
