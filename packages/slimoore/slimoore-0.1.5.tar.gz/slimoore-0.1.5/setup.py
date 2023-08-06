import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='slimoore',
    version='0.1.5',
    # packages=find_packages(),
    include_package_data=True,
    # license='BSD License',  # example license
    description='A simple Django app to conduct Web-based polls.',
    long_description=README,
    url='https://https://github.com/lizidashen/',
    author='sinf',
    author_email='xinguanhua@gmail.com',
    packages=['slimoore'],
    package_dir={'slimoore': 'slimoore'},
)
