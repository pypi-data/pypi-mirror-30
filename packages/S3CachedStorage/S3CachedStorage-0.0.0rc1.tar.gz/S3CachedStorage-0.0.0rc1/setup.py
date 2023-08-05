from unittest import TestLoader
from setuptools import setup, find_packages
from sys import version_info


if not version_info > (3, 4):
    raise Exception('This project requires a Python version greater or equal than 3.5.')


def _get_test_suite():
    test_loader = TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


PKG_NAME = 'S3CachedStorage'


setup(
    author='NyanKiyoshi',
    author_email='hello@vanille.bid',
    url='https://github.com/NyanKiyoshi/%s' % PKG_NAME,
    version='0.0.0rc1',
    name=PKG_NAME,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    keywords=[],
    install_requires=[
        'django-storages',
        'django',
    ],
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only'
    ),
    test_suite='setup._get_test_suite'
)
