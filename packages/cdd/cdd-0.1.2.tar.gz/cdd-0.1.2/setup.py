#from distutils.core import setup
from setuptools import setup

setup(
    name='cdd',
    version='0.1.2',
    packages=['cdd',],
    license='GNU Affero General Public License v3',
    description='improved file system navigation with cd',
    long_description=open('README.txt').read(),
    url='https://github.com/daltonserey/cdd',
    author='Dalton Serey',
    author_email='daltonserey@gmail.com',
    scripts=['bin/cdd', 'bin/cdd.sh'],
)
