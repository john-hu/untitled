import os

from django.conf import settings
from django.http.request import HttpRequest


def get_version(_request: HttpRequest) -> dict:
    version_file = os.path.join(settings.BASE_DIR, 'version')
    version = None
    if os.path.isfile(version_file):
        with open(version_file, 'r') as file:
            version = file.readline()
            file.close()
    return {
        'SILVER_PLATE_VERSION': version if version else 'Unknown'
    }


def is_debug_mode(_request: HttpRequest) -> dict:
    return {"DEBUG": settings.DEBUG}
