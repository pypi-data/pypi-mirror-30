#!/usr/bin/env python

long_description = ""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    pass

sdict = {
    'name': 'django_rundirect',
    'version': "0.3.0",
    'license': 'MIT',
    'packages': ['django_rundirect',
                 'django_rundirect.management',
                 'django_rundirect.management.commands'],
    'package_dir': {'django_rundirect': 'django_rundirect'}, 
    'zip_safe': False,
    'install_requires': ['django'],
    'author': 'Lichun',
    'long_description': long_description,
    'url': 'https://github.com/socrateslee/django_rundirect',
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
