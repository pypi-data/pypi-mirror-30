"""A tool to fetch challenges from a CTFd hosted competition."""

# Always prefer setuptools over distutils
from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ctfdfetch',

    version='0.2.0',

    description='Fetch challenges from a CTFd competition',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://gitlab.com/royragsdale/ctfdfetch',

    author='Roy Ragsdale',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='ctf',
    packages=['ctfdfetch'],

    install_requires=[
        'beautifulsoup4',
        'jinja2',
        'Markdown',
        'requests',
        'tld'],

    entry_points={
        'console_scripts': [
            'ctfdfetch=ctfdfetch.ctfdfetch:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://gitlab.com/royragsdale/ctfdfetch/issues',
        'Source': 'https://gitlab.com/royragsdale/ctfdfetch',
    },

    python_requires='>=3',

    # include templates
    include_package_data=True
)
