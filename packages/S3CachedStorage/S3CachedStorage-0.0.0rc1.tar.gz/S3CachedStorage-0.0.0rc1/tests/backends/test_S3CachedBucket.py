import os
import shutil
from unittest import mock
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.test import TestCase
from S3CachedStorage.backends.S3CachedBucket import S3CachedBucket as BaseStorageCls


class S3BadCachedBucket(BaseStorageCls):
    STORAGE_NAME = 'MY_BUCKET_WITHOUT_SETTINGS'


class S3CachedBucket(BaseStorageCls):
    STORAGE_NAME = 'MY_BUCKET'


class TestS3CachedBucket(TestCase):
    @staticmethod
    def _get_storage_path():
        from django.conf import settings
        path = settings.MY_BUCKET_S3_STORAGE_BACKEND_CACHE_DIR
        return path

    @classmethod
    def _clean_storage(cls):
        path = cls._get_storage_path()
        if os.path.isdir(path):
            shutil.rmtree(path)
        os.mkdir(path)

    def setUp(self):
        self._clean_storage()
        self.storage = S3CachedBucket()  # type: S3CachedBucket
        self.storage._connections.connection = mock.MagicMock()
        super(TestS3CachedBucket, self).setUp()

    def _create_non_cached_file(self, name):
        content = ContentFile('Hi')
        self.storage.save(name, content)

        # remove cached file
        os.remove(self.storage._local_storage.path(name))

    def test_init_miss_configured(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'You must override STORAGE_NAME.'):
            BaseStorageCls()

        with self.assertRaisesMessage(
                ImproperlyConfigured,
                'You must provide '
                'settings.MY_BUCKET_WITHOUT_SETTINGS_S3_STORAGE_BACKEND_CACHE_DIR'):
            S3BadCachedBucket()

    def test_init_correctly_configured(self):
        path = self._get_storage_path()
        assert self.storage._local_cache_path == path

    def test_storage_open(self):
        name = 'test/file.txt'
        self._create_non_cached_file(name)
        from storages.backends.s3boto3 import S3Boto3Storage

        with mock.patch.object(S3Boto3Storage, 'open') as mocked:
            mocked.return_value = ContentFile('Hi')

            assert not self.storage._exists_local(name)
            file = self.storage.open(name)
            assert file.read() == 'Hi'
            assert self.storage._exists_local(name)

            with open(self.storage._local_storage.path(name), 'w') as fp:
                fp.write('I was cached!')

            file = self.storage.open(name)
            assert file.read() == b'I was cached!'

    def test_storage_delete(self):
        name = 'test/file.txt'
        content = ContentFile('Hi')
        self.storage.save(name, content)

        mocked_local_delete = self.storage._local_storage.delete = mock.Mock(
            wraps=self.storage._local_storage.delete)

        self.storage.delete(name)
        self.storage.bucket.Object.assert_called_with(name)
        self.storage.bucket.Object.return_value.delete.assert_called_with()
        mocked_local_delete.assert_called_once()

    def test_storage_delete_non_cached(self):
        name = 'test/file.txt'
        self._create_non_cached_file(name)

        mocked_local_delete = self.storage._local_storage.delete = mock.Mock(
            wraps=self.storage._local_storage.delete)

        self.storage.delete(name)
        self.storage.bucket.Object.assert_called_with(name)
        self.storage.bucket.Object.return_value.delete.assert_called_with()

        # no local file should have been removed since nothing is cached
        mocked_local_delete.assert_not_called()

    def test_file_open_doesnt_create_file_if_exists(self):
        name = 'test/file.txt'
        content = ContentFile('Hi')
        expected_path = os.path.join(self.storage._local_cache_path, 'test', 'file.txt')

        mocked_save_to_local_storage = self.storage._save_to_local_storage = mock.Mock(
            wraps=self.storage._save_to_local_storage)

        self.storage.save(name, content)
        mocked_save_to_local_storage.assert_called_once()

        assert self.storage._local_storage.exists(name)
        assert self.storage._local_storage.path(name) == expected_path
        assert self.storage._local_storage.open(name).read() == b'Hi'

        with mock.patch.object(self.storage, '_save_to_local_storage') as method:
            self.storage.open('test/file.txt')
            method.assert_not_called()

    def test_storage_save(self):
        """
        Test saving a gzipped file
        """
        self.storage._local_storage = mock.MagicMock()
        name = 'test/test_storage_save.gz'
        content = ContentFile("I am gzip'd")
        self.storage.save(name, content)
        obj = self.storage.bucket.Object.return_value
        obj.upload_fileobj.assert_called_with(
            content.file,
            ExtraArgs={
                'ContentType': 'application/octet-stream',
                'ContentEncoding': 'gzip',
                'ACL': self.storage.default_acl,
            }
        )
        self.storage._local_storage.save.assert_called_once_with(name, content)
