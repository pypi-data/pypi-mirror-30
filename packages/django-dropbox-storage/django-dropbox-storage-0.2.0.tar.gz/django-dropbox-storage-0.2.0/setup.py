#!/usr/bin/env python
from os import path
from codecs import open
from setuptools import setup, find_packages
from django_dropbox_storage import version

packages = find_packages(exclude=['contrib', 'docs', 'tests'])

requires = [
    'django>=1.11',
    'dropbox>=8.0.0',
]

project_url = 'https://github.com/zuck/django-dropbox-storage'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-dropbox-storage',
    version=version,
    description='A Dropbox Storage for your Django apps',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=u'Emanuele Bertoldi',
    author_email='emanuele.bertoldi@gmail.com',
    url=project_url,
    download_url=project_url + '/archive/' + version + '.tar.gz',
    packages=packages,
    install_requires=requires,
    keywords = 'django storage dropbox',
    license='MIT',
)
