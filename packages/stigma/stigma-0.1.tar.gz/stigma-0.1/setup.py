from distutils.core import setup
from setuptools import setup

def readme():
    with open('README.rst') as f:
         return f.read()

setup(name = 'stigma',
      version = '0.1',
      description ='Signal Processing of LC-MS Data',
      author = 'Kundai Sachikonye',
      author_email = 'k.sachikonye@uke.de',
      license = 'MIT',
      install_requires =['pymzml', 'scipy', 'numpy','matplotlib'],
      test_suite = 'nose.collector',
      tests_require = ['nose', 'nose-cover3'],
      include_package_data = True,
      zip_safe= False )