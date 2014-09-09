from __future__ import unicode_literals
from setuptools import setup
import re, os

dependencies = []
f = open(os.path.join(os.path.dirname(__file__), 'smartsearch_requirements.txt'))
for line in f:
      li=line.strip()
      if not (re.match("^[\s]*$", li) or re.match("^#.*", li)):
          dependencies.append(li)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-smartsearch',
    version='0.1.0',
    author='Joe Jasinski',
    author_email='jjasinski@imagescape.com',
    url='',
    description='Search frontend tool.', 
    install_requires=[
       'django >= 1.6',
    ],
    long_description=read('README.md'),
    install_requires=dependencies,
)