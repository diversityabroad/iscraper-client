from setuptools import setup, find_packages

NAME = 'django-smartsearch'
VERSION = '0.1.1'
AUTHOR = 'Imaginary Landscape'
DESCRIPTION = ''
LONG_DESCRIPTION = ""

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=('Framework :: Django'),
    url='',
    include_package_data=True,
    install_requires=(
        'google-api-python-client'
    ),
)
