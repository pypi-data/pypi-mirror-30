"""A tool to fetch challenges from a CTFd hosted competition."""

# Always prefer setuptools over distutils
from setuptools import setup

setup(
    name='ctfdfetch',

    version='0.1.0',

    description='Fetch challenges from a CTFd competition',

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
)
