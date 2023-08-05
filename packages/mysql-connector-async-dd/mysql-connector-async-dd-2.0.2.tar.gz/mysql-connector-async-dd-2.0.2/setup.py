#!/usr/bin/python

import os
from setuptools import setup, find_packages



def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


META_DATA = {
    'name': 'mysql-connector-async-dd',
    'version': "2.0.2",
    'description': "mysql async connection",
    'long_description': read('README.md'),
    'license': 'MIT',

    'author': "Devin",
    'author_email': "waipbmtd@gmail.com",

    'url': "https://github.com/waipbmtd/django-weed",

    'packages': find_packages(),

    'install_requires': ('mysql-connector-python-dd>=2.0.2'),
}

if __name__ == "__main__":
    setup(**META_DATA)

