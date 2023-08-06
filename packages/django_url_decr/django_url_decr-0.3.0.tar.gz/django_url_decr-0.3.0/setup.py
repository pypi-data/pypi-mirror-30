#!/usr/bin/env python

long_description = ""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    pass

sdict = {
    'name': 'django_url_decr',
    'version': "0.3.0",
    'packages': ['django_url_decr'],
    'zip_safe': False,
    'install_requires': ['django'],
    'author': 'Lichun',
    'url': 'https://github.com/socrateslee/django_url_decr',
    'long_description': long_description,
    'classifiers': [
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
