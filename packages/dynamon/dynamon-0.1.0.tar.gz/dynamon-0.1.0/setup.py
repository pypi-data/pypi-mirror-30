from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='dynamon',
      version='0.1.0',
      description='Python API for dynamon.io',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/dynamon-io/dynamon-python',
      author='Viktor Qvarfordt',
      author_email='viktor.qvarfordt@gmail.com',
      license='MIT',
      packages=['dynamon'],
      install_requires=['requests']
)
