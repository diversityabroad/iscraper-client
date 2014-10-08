from __future__ import unicode_literals
from setuptools import setup
import re
import os

dependencies = []
f = open(os.path.join(os.path.dirname(__file__),
                      'smartsearch_requirements.txt'))
for line in f:
    li = line.strip()
    if not (re.match("^[\s]*$", li) or re.match("^#.*", li)):
        dependencies.append(li)

setup(
    name='django-smartsearch',
    version='0.1.1',
    author='Joe Jasinski',
    author_email='jjasinski@imagescape.com',
    url='git@git.imagescape.com:smartsearch2',
    description='Search frontend tool.',
    install_requires=dependencies,
)
