from setuptools import setup, find_packages

NAME = 'iscraper_client'
VERSION = '1.0.0'
AUTHOR = 'Imaginary Landscape'
DESCRIPTION = 'Client application for interacting with iscraper.imagescape.com'
LONG_DESCRIPTION = ""

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=('Framework :: Django'),
    url='',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=(
        'requests'
    ),
    extras_require=({
        'google': [
            'google-api-python-client',
        ]
    }),
)
