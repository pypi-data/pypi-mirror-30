from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hatchbuck',
      version='1.0.3',
      description='Hatchbuck.com CRM API bindings for python',
      long_description=long_description,
      keywords='hatchbuck CRM API',
      url='https://github.com/vshn/python-hatchbuck',
      author='VSHN AG, Bashar Said',
      author_email='bashar.said@vshn.ch',
      # BSD 3-Clause License:
      # - http://opensource.org/licenses/BSD-3-Clause
      license = 'BSD',
      py_modules=["hatchbuck"],
      install_requires = [
            'requests>=2',
            'pycountry>=1',
      ],
)
