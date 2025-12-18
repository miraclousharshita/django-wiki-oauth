from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from mwclient import Site
from social_django.models import UserSocialAuth

from .models import WikiPage, WikiActor, WikiRevision


def index(request):
    context = {}
    return render(request, 'user_profile/index.dtl', context)

@login_required
def profile(request):
    mw_username = None
    user_info = None
    error = None
    wiki_stats = {}

    try:
        social_auth = request.user.social_auth.get(provider="mediawiki")

        mw_username = (
                social_auth.extra_data.get('username') or
                social_auth.extra_data.get('user', {}).get('name') or
                None
        )

        token_blob = social_auth.extra_data.get("access_token") or {}
        if isinstance(token_blob, dict):
            access_key = token_blob.get("oauth_token") or token_blob.get("key")
            access_secret = token_blob.get("oauth_token_secret") or token_blob.get("secret")
        else:
            access_key = token_blob
            access_secret = social_auth.extra_data.get("access_token_secret")

        if not access_key or not access_secret:
            raise ValueError("Missing OAuth access token/secret")

        parsed_url = urlparse(settings.SOCIAL_AUTH_MEDIAWIKI_URL)
        host = parsed_url.netloc
        path = '/w/'

        site = Site(
            host,
            path=path,
            consumer_token=settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
            consumer_secret=settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
            access_token=access_key,
            access_secret=access_secret
        )

        result = site.get('query', meta='userinfo', uiprop='email|groups|rights')
        user_info = result.get('query', {}).get('userinfo', {})

        if not mw_username:
            mw_username = user_info.get('name')
            if mw_username:
                social_auth.extra_data['username'] = mw_username
                social_auth.save()

        try:
            if 'wiki_replica' in settings.DATABASES:
                total_articles = WikiPage.objects.using('wiki_replica').filter(
                    page_namespace=0,
                    page_is_redirect=False
                ).count()

                user_edit_count = 0
                if mw_username:
                    username_bytes = mw_username.encode('utf-8') if isinstance(mw_username, str) else mw_username
                    actor = WikiActor.objects.using('wiki_replica').filter(
                        actor_name=username_bytes
                    ).first()

                    if actor:
                        user_edit_count = WikiRevision.objects.using('wiki_replica').filter(
                            rev_actor=actor.actor_id
                        ).count()

                wiki_stats = {
                    'total_articles': total_articles,
                    'user_edit_count': user_edit_count,
                }
            else:
                wiki_stats = {
                    'total_articles': 'N/A (local dev)',
                    'user_edit_count': 'N/A (local dev)',
                }
        except Exception as wiki_error:
            error = f"Wiki replica query error: {str(wiki_error)}"

    except UserSocialAuth.DoesNotExist:
        error = "No MediaWiki social-auth record for this user."
    except Exception as e:
        error = f"Error: {str(e)}"

    context = {
        "mw_username": mw_username,
        "user_info": user_info,
        "error": error,
        "wiki_stats": wiki_stats,
    }
    return render(request, "user_profile/profile.dtl", context)

def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)


def search_articles(request):
    """
    Search for articles in the wiki replica database.
    """
    results = []
    search_query = ""
    limit = 10
    namespace = 0
    exclude_redirects = True
    error = None

    if request.method == "GET" and request.GET.get('q'):
        search_query = request.GET.get('q', '').strip()
        try:
            limit = min(int(request.GET.get('limit', 10)), 100)
        except ValueError:
            limit = 10

        try:
            namespace = int(request.GET.get('namespace', 0))
        except ValueError:
            namespace = 0

        exclude_redirects = request.GET.get('exclude_redirects') == 'on'

        try:
            if 'wiki_replica' not in settings.DATABASES:
                error = "Search is only available on Toolforge (wiki replica database not configured locally)"
            else:
                query = WikiPage.objects.using('wiki_replica').filter(
                    page_namespace=namespace
                )

                if search_query:
                    search_term = search_query.replace(' ', '_')
                    query = query.filter(page_title__contains=search_term)

                if exclude_redirects:
                    query = query.filter(page_is_redirect=False)

                results = list(query[:limit])

        except Exception as e:
            error = f"Search error: {str(e)}"
            import traceback
            traceback.print_exc()

    context = {
        'results': results,
        'search_query': search_query,
        'limit': limit,
        'namespace': namespace,
        'exclude_redirects': exclude_redirects,
        'error': error,
    }
    return render(request, 'user_profile/search.dtl', context)

@login_required
def vue_app(request):
    return render(request, 'user_profile/vue/app.dtl')