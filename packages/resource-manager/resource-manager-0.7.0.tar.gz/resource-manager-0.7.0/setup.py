from distutils.core import setup
from setuptools import find_packages

classifiers = '''Development Status :: 5 - Production/Stable
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6'''

with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

version = '0.7.0'

setup(
    name='resource-manager',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    version=version,
    description='A small resource manager for config files',
    long_description=long_description,
    author='maxme1',
    author_email='maxs987@gmail.com',
    license='MIT',
    url='https://github.com/maxme1/resource-manager',
    download_url='https://github.com/maxme1/resource-manager/archive/%s.tar.gz' % version,
    keywords=[
        'config', 'manager', 'resource'
    ],
    classifiers=classifiers.splitlines(),
    install_requires=[]
)
