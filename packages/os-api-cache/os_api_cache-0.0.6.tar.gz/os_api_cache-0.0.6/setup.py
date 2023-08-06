import os
from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='os_api_cache',
    version='0.0.6',
    description=(
        'Manage a cache for OpenSpending API'
    ),
    long_description=long_description,

    url='https://github.com/openspending/os-api-cache',

    author='Open Knowledge International',
    author_email='info@okfn.org',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='fdp fiscal data api openspending cache',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        "redis",
    ],
    requires=[
        "pytest"
    ]
)
