from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage

from S3CachedStorage.utils import get_key_from_settings

BASE_CACHE_SETTING_KEY = 'S3_STORAGE_BACKEND_CACHE_DIR'


class S3CachedBucket(S3Boto3Storage):
    STORAGE_NAME = None

    def __init__(self, *args, **kwargs):
        self._local_cache_path = None  # type: str
        self._local_storage = None  # type: FileSystemStorage

        if not self.STORAGE_NAME:
            raise ImproperlyConfigured('You must override STORAGE_NAME.')

        super().__init__(*args, **kwargs)
        self._set_local_storage()

    def _set_local_storage(self):
        self._local_cache_path = get_key_from_settings(self.STORAGE_NAME, BASE_CACHE_SETTING_KEY)
        self._local_storage = FileSystemStorage(self._local_cache_path)

    def _save_to_local_storage(self, name, content):
        self._local_storage.save(name, content)

    def _exists_local(self, name):
        return self._local_storage.exists(name)

    def _delete_local(self, name):
        return self._local_storage.delete(name)

    def exists(self, name):
        return self._exists_local(name) or super(S3CachedBucket, self).exists(name)

    def save(self, name, content, max_length=None):
        ret = super(S3CachedBucket, self).save(name, content, max_length)
        self._save_to_local_storage(name, content)
        return ret

    def open(self, name, mode='rb'):
        if self._exists_local(name):
            file = self._local_storage.open(name, mode)
        else:
            file = super(S3CachedBucket, self).open(name, mode)
            self._save_to_local_storage(name, file)
            file.seek(0)
        return file

    def delete(self, name):
        ret = super(S3CachedBucket, self).delete(name)
        if self._exists_local(name):
            self._delete_local(name)
        return ret
