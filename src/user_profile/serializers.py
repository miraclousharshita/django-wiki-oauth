from rest_framework import serializers


class UserInfoSerializer(serializers.Serializer):
    """Serializer for user information."""
    username = serializers.CharField()
    mw_username = serializers.CharField(allow_null=True)
    user_id = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField(allow_null=True, required=False)
    groups = serializers.ListField(child=serializers.CharField())
    rights_count = serializers.IntegerField()


class WikiStatsSerializer(serializers.Serializer):
    """Serializer for Wikipedia statistics."""
    total_articles = serializers.IntegerField(required=False)
    user_edit_count = serializers.IntegerField(required=False)


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search results."""
    page_id = serializers.IntegerField()
    page_title = serializers.CharField()
    page_namespace = serializers.IntegerField()
    page_is_redirect = serializers.BooleanField()
    page_len = serializers.IntegerField()
    url = serializers.CharField()