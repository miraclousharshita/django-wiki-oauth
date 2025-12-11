from urllib.parse import urlparse

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
import pywikibot
from pywikibot.login import OauthLoginManager

def index(request):
    context = {}
    return render(request, 'user_profile/index.dtl', context)



@login_required
def profile(request):
    site = None
    site_user = None
    error = None

    try:
        social_auth = request.user.social_auth.get(provider="mediawiki")

        token_blob = social_auth.extra_data.get("access_token") or {}
        if isinstance(token_blob, dict):
            access_key = token_blob.get("oauth_token") or token_blob.get("key")
            access_secret = token_blob.get("oauth_token_secret") or token_blob.get("secret")
        else:
            # Some backends store oauth1 tokens differently
            access_key = token_blob
            access_secret = social_auth.extra_data.get("access_token_secret")

        if not access_key or not access_secret:
            raise ValueError("Missing OAuth access token/secret in social_auth.extra_data")

        mw_username = social_auth.extra_data.get("username") or request.user.username
        pywikibot.config.usernames['commons']['beta'] = mw_username

        site = pywikibot.Site("beta", "commons", user=mw_username)

        oauth = OauthLoginManager(
            site=site,
            user=settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
            password=settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
        )
        oauth.access_token = (access_key, access_secret)

        hostname = urlparse(site.base_url("")).netloc
        pywikibot.config.authenticate[hostname] = (
            *oauth.consumer_token,
            *oauth.access_token,
        )

        site.login()
        site_user = site.user()

    except UserSocialAuth.DoesNotExist:
        error = "No MediaWiki social-auth record for this user."
    except Exception as e:
        error = str(e)

    context = {
        "pywikibot_user": str(site_user) if site_user else None,
        "pywikibot_error": error,
    }
    return render(request, "user_profile/profile.dtl", context)

def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)