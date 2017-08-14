from setuptools import setup, find_packages

NAME = 'django-smartsearch'
VERSION = '3.0.3'
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
