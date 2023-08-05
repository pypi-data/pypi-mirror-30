from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='itsjustcode',
      version='0.1.0a1',
      description='Database First Code Generator that uses the SQL Alchemy and Jinja2',
      long_description=long_description,
      url='https://github.com/ellerbus/itsjustcode',
      license='MIT',
      keywords='codegenerator development',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      install_requires=['sqlalchemy', 'jinja2'],
      packages=['itsjustcode'],
      zip_safe=False)
