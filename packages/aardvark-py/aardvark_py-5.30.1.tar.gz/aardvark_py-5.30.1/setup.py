"""Total Phase Aardvark Python API.

See:
http://www.totalphase.com/products/aardvark-software-api
"""

import os, re, codecs
import unittest

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# from https://github.com/pypa/pip/blob/develop/setup.py
def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()

# from https://github.com/pypa/pip/blob/develop/setup.py
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

setup(
    name='aardvark_py',
    version=find_version('aardvark_py', '__init__.py'),
    description='Total Phase Aardvark Python API',
    long_description=read('README.rst'),
    url='https://github.com/FlyingCampDesign/aardvark_py.git',
    author='Flying Camp Design',
    author_email='support@flyingcampdesign.com',
    license='Proprietary License (see LICENSE.txt provided with the distribution)',
    keywords='development I2C SPI',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Embedded Systems',
    ],

    packages=find_packages(exclude=['docs', 'tests']),
    extras_require={
        'dev': [
            'wheel',
            'twine',
            'docutils',
            'pygments',
            'sphinx>=1.7.0',
            'sphinx_rtd_theme',
        ],
    },
    include_package_data = True,
    zip_safe=False,
    test_suite='tests.test_suite',
)
