# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_addon import __version__


setup(
    name="django-addon",
    version=__version__,
    description='An opinionated Django setup bundled as an Addon',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/django-addons/django-addon',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'django-addons>=2',
        'Django==2.0.3',

        # setup utils
        'dj-database-url',
        'dj-email-url',
        'dj-redis-url',
        'django-cache-url',
        'django-getenv',
        'yurl',

        # error reporting
        'raven',

        # wsgi server related
        'uwsgi',
        'dj-static',

        # database
        'psycopg2',
        'click',

        # storage
        'django-storages',
        'boto>=2.40.0',

        # helpers
        'aldryn-sites>=0.5.6',

        'easy-thumbnails>=2.2.1.1',
    ],
    entry_points='''
        [console_scripts]
        django-addon=django_addon.cli:main
    ''',
    include_package_data=True,
    zip_safe=False,
)
