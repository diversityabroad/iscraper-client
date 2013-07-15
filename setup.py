from distutils.core import setup
import re, os

dependencies = []
f = open(os.path.join(os.path.dirname(__file__), 'smartsearch_requirements.txt'))
for line in f:
      li=line.strip()
      if not (re.match("^[\s]*$", li) or re.match("^#.*", li)):
          dependencies.append(li)

setup(
    name='django-smartsearch',
    version='0.1.0',
    author='Joe Jasinski',
    author_email='jjasinski@imagescape.com',
    url='',
    description='',
    long_description=open('README.md').read(),
    install_requires=dependencies,
)