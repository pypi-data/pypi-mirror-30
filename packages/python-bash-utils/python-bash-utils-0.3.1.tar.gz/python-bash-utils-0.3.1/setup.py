# http://setuptools.readthedocs.org/en/latest/setuptools.html
from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

__version__ = '0.3.1'

setup(
    name='python-bash-utils',
    version=__version__,

    description='A package which allows making bash style command line scripts easier.',
    long_description=long_description,

    url='https://bitbucket.org/tsantor/python-bash-utils',
    download_url='https://bitbucket.org/tsantor/python-bash-utils/get/%s.tar.gz' % __version__,
    author='Tim Santor',
    author_email='tsantor@xstudios.agency',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        "Environment :: Console",

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='bash utils colors log',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'colorama>=0.3.9,<4',
        'six>=1.11.0,<2',
    ],

    # Tests
    test_suite='nose.collector',
    tests_require=['nose'],
)
