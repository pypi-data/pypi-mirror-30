#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as f:
    long_description = f.read()

setup(
    name='ConfMerge',
    version='0.2.0',
    author='Andre Lehmann',
    author_email='aisberg@posteo.de',
    url='https://github.com/Aisbergg/python-confmerge',
    license='LGPL',
    description='Configuration file merge utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='config ini yaml json command-line CLI',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Aisbergg/python-confmerge/issues',
        'Source': 'https://github.com/Aisbergg/python-confmerge',
    },
    packages=find_packages(exclude=['examples']),
    entry_points={
        'console_scripts': [
            'confmerge = confmerge:cli',
        ]
    },
    install_requires=[
        'pyyaml',
    ],
    include_package_data=True,
    zip_safe=True,
    platforms=['POSIX'],
)
