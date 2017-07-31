from distutils.core import setup

NAME = 'django-smartsearch'
VERSION = '0.1.1'
AUTHOR = 'Imaginary Landscape'
DESCRIPTION = ''
LONG_DESCRIPTION = long_description = open('README.md').read(),

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
