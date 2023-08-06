import sys
import unittest
from codecs import open
from os import path

from setuptools import find_packages, setup

import versioneer

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("mangrove.tests", pattern="*.py")
    return test_suite

setup(
    name='mangrove-surface-sdk',

    version=versioneer.get_version(),

    description='Mangrove Surface SDK',
    long_description=long_description,

    url='https://github.com/mangroveai/mangrove-surface-python-sdk',
    # download_url='https://github.com/wnkz/shipami/archive/{}.tar.gz'.format(__version__),

    author='Mangrove',
    contact_email='contact@mangrove.ai',
    author_email='contact@mangrove.ai',

    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,

    install_requires=[
        'requests>=2.12.3',
        'requests-toolbelt>=0.7.0',
        'clint>=0.5.1',
        'humanize>=0.5.1',
        'funcsigs>=1.0.2',
        'boto3>=1.4.4'
    ],

    cmdclass=versioneer.get_cmdclass(),

    test_suite='setup.test_suite',
    tests_require=[
        'pact-python>=0.7.0'
    ],

    zip_safe=False
)
