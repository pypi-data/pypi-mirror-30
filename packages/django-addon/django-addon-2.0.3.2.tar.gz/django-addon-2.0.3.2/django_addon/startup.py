import os

import django.core.management

from getenv import env


def manage(path):
    _setup()
    utility = django.core.management.ManagementUtility(None)
    utility.execute()


def wsgi(path):
    _setup()
    from django.core.wsgi import get_wsgi_application
    from django.conf import settings
    from dj_static import Cling, MediaCling
    app = get_wsgi_application()
    if settings.ENABLE_SYNCING:
        if not settings.STATIC_URL_IS_ON_OTHER_DOMAIN:
            app = Cling(app)
        if not settings.MEDIA_URL_IS_ON_OTHER_DOMAIN:
            app = MediaCling(app)
    return app


def setup(path):
    _setup()
    import django
    django.setup()


def _setup():
    os.environ['DJANGO_SETTINGS_MODULE'] = env(
        'DJANGO_SETTINGS_MODULE', 'settings'
    )
