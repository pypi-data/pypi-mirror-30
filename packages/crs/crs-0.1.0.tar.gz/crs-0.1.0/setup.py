from os.path import abspath
from os.path import dirname
from os.path import join

from setuptools import setup

__author__ = 'Gregory Halverson'

NAME = 'crs'
EMAIL = 'gregory.halverson@gmail.com'
URL = 'http://github.com/gregory-halverson/crs'
CLASSIFIERS = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

with open(join(abspath(dirname(__file__)), NAME, 'version.txt')) as f:
    __version__ = f.read()

with open(join(abspath(dirname(__file__)), 'README.md')) as f:
    long_description = f.read()

with open(join(abspath(dirname(__file__)), 'requirements.txt')) as f:
    requirements = f.readlines()

setup(
    name=NAME,
    version=__version__,
    description="Geographic Coordinate Reference System Encapsulation and Conversion",
    author=__author__,
    author_email=EMAIL,
    url=URL,
    packages=['crs'],
    include_package_data=True,
    install_requires=requirements,
    long_description=long_description,
    package_data={'crs': ['*.txt']},
    license='MIT',
    classifiers=CLASSIFIERS,
    keywords='geography coordinates projections'
)
