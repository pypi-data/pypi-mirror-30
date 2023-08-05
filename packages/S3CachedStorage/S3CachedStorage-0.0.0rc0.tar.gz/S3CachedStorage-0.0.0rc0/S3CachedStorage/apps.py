from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class S3CachedStorageConfig(AppConfig):
    name = 'S3CachedStorage'
    verbose_name = _("S3 Cached Storage")
