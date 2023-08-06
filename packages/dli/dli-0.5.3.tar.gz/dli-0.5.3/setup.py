"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from dli import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=skele', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name='dli',
    version=__version__,
    description='Data Lake command line Interface.',
    long_description=long_description,
    url='https://git.mdevlab.com/data-lake/data-lake-sdk',
    author='Ashic Mahtab',
    author_email='ashic@heartysoft.com',
    license='MOZ-2',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli, datalake, data, lake',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['docopt', 'pyyaml', 'requests', 's3fs', 'pandas', 'pypermedia', 'future'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'dli=dli.dli:main',
        ],
    },
    cmdclass={'test': RunTests},
)
