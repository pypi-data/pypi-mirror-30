# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_addons_formlib import __version__

setup(
    name='django-addons-formlib',
    version=__version__,
    description='django-addons Framework form library',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/django-addons/django-addons-formlib',
    packages=find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
)
