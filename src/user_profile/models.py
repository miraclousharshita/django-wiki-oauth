from django.db import models


class WikiPage(models.Model):
    """
    Django model mapping to MediaWiki's 'page' table.
    """

    page_id = models.IntegerField(primary_key=True)
    page_namespace = models.IntegerField()
    page_title = models.CharField(max_length=255)
    page_is_redirect = models.BooleanField()
    page_is_new = models.BooleanField()
    page_random = models.FloatField()
    page_touched = models.CharField(max_length=14)
    page_links_updated = models.CharField(max_length=14, null=True, blank=True)
    page_latest = models.IntegerField()
    page_len = models.IntegerField()
    page_content_model = models.CharField(max_length=32, null=True, blank=True)
    page_lang = models.CharField(max_length=35, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "page"

    def __str__(self):
        return self.full_title

    @property
    def full_title(self):
        """Returns the page title with underscores replaced by spaces"""
        return (
            self.page_title.decode("utf-8").replace("_", " ")
            if isinstance(self.page_title, bytes)
            else self.page_title.replace("_", " ")
        )

    @property
    def url(self):
        """Returns the URL to view this page"""
        namespace_names = {0: "", 6: "File:", 14: "Category:"}
        ns_prefix = namespace_names.get(
            self.page_namespace, f"NS{self.page_namespace}:"
        )
        title = (
            self.page_title.decode("utf-8")
            if isinstance(self.page_title, bytes)
            else self.page_title
        )
        return f"https://en.wikipedia.org/wiki/{ns_prefix}{title}"


class WikiRevision(models.Model):
    """
    Django model mapping to MediaWiki's 'revision' table.
    """

    rev_id = models.IntegerField(primary_key=True)
    rev_page = models.IntegerField()
    rev_comment_id = models.BigIntegerField()
    rev_actor = models.BigIntegerField()
    rev_timestamp = models.CharField(max_length=14)
    rev_minor_edit = models.BooleanField()
    rev_deleted = models.IntegerField()
    rev_len = models.IntegerField(null=True, blank=True)
    rev_parent_id = models.IntegerField(null=True, blank=True)
    rev_sha1 = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = "revision"

    def __str__(self):
        return f"Revision {self.rev_id}"


class WikiActor(models.Model):
    """
    Django model mapping to MediaWiki's 'actor' table.
    Links revisions to users.
    """

    actor_id = models.BigIntegerField(primary_key=True)
    actor_user = models.IntegerField(null=True, blank=True)
    actor_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "actor"

    def __str__(self):
        return (
            self.actor_name.decode("utf-8")
            if isinstance(self.actor_name, bytes)
            else self.actor_name
        )
