from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from mwclient import Site
from social_django.models import UserSocialAuth


def index(request):
    context = {}
    return render(request, 'user_profile/index.dtl', context)


@login_required
def profile(request):
    mw_username = None
    user_info = None
    error = None

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

    except UserSocialAuth.DoesNotExist:
        error = "No MediaWiki social-auth record for this user."
    except Exception as e:
        error = f"Error: {str(e)}"

    context = {
        "mw_username": mw_username,
        "user_info": user_info,
        "error": error,
    }
    return render(request, "user_profile/profile.dtl", context)

def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)