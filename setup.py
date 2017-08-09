from setuptools import setup, find_packages

NAME = 'django-smartsearch'
VERSION = '0.1.4'
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
    package_data={'templates': ['*'], 'static': ['*']},
    zip_safe=False,
    include_package_data=True,
    install_requires=(
        'google-api-python-client',
        'requests'
    ),
)
