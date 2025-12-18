from urllib.parse import urlparse

from django.conf import settings
from mwclient import Site
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth

from .models import WikiActor, WikiPage, WikiRevision
from .serializers import SearchResultSerializer, UserInfoSerializer, WikiStatsSerializer


class UserInfoAPIView(APIView):
    """API endpoint for user information."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            social_auth = request.user.social_auth.get(provider="mediawiki")

            mw_username = (
                social_auth.extra_data.get("username")
                or social_auth.extra_data.get("user", {}).get("name")
                or None
            )

            token_blob = social_auth.extra_data.get("access_token") or {}
            if isinstance(token_blob, dict):
                access_key = token_blob.get("oauth_token") or token_blob.get("key")
                access_secret = token_blob.get("oauth_token_secret") or token_blob.get(
                    "secret"
                )
            else:
                access_key = token_blob
                access_secret = social_auth.extra_data.get("access_token_secret")

            if not access_key or not access_secret:
                return Response(
                    {"error": "Missing OAuth credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            parsed_url = urlparse(settings.SOCIAL_AUTH_MEDIAWIKI_URL)
            host = parsed_url.netloc
            path = "/w/"

            site = Site(
                host,
                path=path,
                consumer_token=settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
                consumer_secret=settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
                access_token=access_key,
                access_secret=access_secret,
            )

            result = site.get("query", meta="userinfo", uiprop="email|groups|rights")
            user_info = result.get("query", {}).get("userinfo", {})

            if not mw_username:
                mw_username = user_info.get("name")
                if mw_username:
                    social_auth.extra_data["username"] = mw_username
                    social_auth.save()

            data = {
                "username": request.user.username,
                "mw_username": mw_username,
                "user_id": user_info.get("id"),
                "email": user_info.get("email"),
                "groups": user_info.get("groups", []),
                "rights_count": len(user_info.get("rights", [])),
            }

            serializer = UserInfoSerializer(data)
            return Response(serializer.data)

        except UserSocialAuth.DoesNotExist:
            return Response(
                {"error": "No MediaWiki social-auth record"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WikiStatsAPIView(APIView):
    """API endpoint for Wikipedia statistics."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if "wiki_replica" not in settings.DATABASES:
                data = {
                    "total_articles": "N/A",
                    "user_edit_count": "N/A",
                }
                return Response(data)

            social_auth = request.user.social_auth.get(provider="mediawiki")
            mw_username = social_auth.extra_data.get("username")

            total_articles = (
                WikiPage.objects.using("wiki_replica")
                .filter(page_namespace=0, page_is_redirect=False)
                .count()
            )

            user_edit_count = 0
            if mw_username:
                username_bytes = (
                    mw_username.encode("utf-8")
                    if isinstance(mw_username, str)
                    else mw_username
                )
                actor = (
                    WikiActor.objects.using("wiki_replica")
                    .filter(actor_name=username_bytes)
                    .first()
                )

                if actor:
                    user_edit_count = (
                        WikiRevision.objects.using("wiki_replica")
                        .filter(rev_actor=actor.actor_id)
                        .count()
                    )

            data = {
                "total_articles": total_articles,
                "user_edit_count": user_edit_count,
            }

            serializer = WikiStatsSerializer(data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchAPIView(APIView):
    """API endpoint for searching Wikipedia articles."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.GET.get("q", "").strip()

        if not search_query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "wiki_replica" not in settings.DATABASES:
            return Response(
                {"error": "Search only available on Toolforge"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            limit = min(int(request.GET.get("limit", 10)), 100)
        except ValueError:
            limit = 10

        try:
            namespace = int(request.GET.get("namespace", 0))
        except ValueError:
            namespace = 0

        exclude_redirects = (
            request.GET.get("exclude_redirects", "true").lower() == "true"
        )

        try:
            query = WikiPage.objects.using("wiki_replica").filter(
                page_namespace=namespace
            )

            if search_query:
                search_term = search_query.replace(" ", "_")
                query = query.filter(page_title__contains=search_term)

            if exclude_redirects:
                query = query.filter(page_is_redirect=False)

            results = list(query[:limit])

            results_data = []
            for page in results:
                results_data.append(
                    {
                        "page_id": page.page_id,
                        "page_title": page.full_title,
                        "page_namespace": page.page_namespace,
                        "page_is_redirect": page.page_is_redirect,
                        "page_len": page.page_len,
                        "url": page.url,
                    }
                )

            serializer = SearchResultSerializer(results_data, many=True)
            return Response(
                {
                    "results": serializer.data,
                    "count": len(results),
                    "query": search_query,
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
