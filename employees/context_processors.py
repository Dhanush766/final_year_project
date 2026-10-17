"""Makes a few project-wide values available in every template."""
from django.conf import settings


def site_settings(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL,
    }
