from setuptools import setup


setup(name='dynamon',
      version='0.1.1',
      description='Python API for dynamon.io',
      long_description='Python API for dynamon.io\n\nGitHub: https://github.com/dynamon-io/dynamon-python',
      url='https://github.com/dynamon-io/dynamon-python',
      author='Viktor Qvarfordt',
      author_email='viktor.qvarfordt@gmail.com',
      packages=['dynamon'],
      install_requires=['requests']
)
