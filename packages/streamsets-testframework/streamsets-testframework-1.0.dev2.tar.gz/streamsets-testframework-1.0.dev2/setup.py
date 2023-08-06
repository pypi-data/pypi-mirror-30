#!/usr/bin/env python
# Copyright 2018 StreamSets Inc.

"""The setup script."""

from setuptools import setup

requirements = [
    'docker',
    'streamsets',
]

setup(
    name='streamsets-testframework',
    version='1.0.dev2',
    description='A test framework for StreamSets products',
    author='StreamSets, Inc.',
    author_email='eng-productivity@streamsets.com',
    packages=['streamsets.testframework.cli'],
    entry_points={'console_scripts': ['streamsets-testframework = streamsets.testframework.cli:main',
                                      'stf = streamsets.testframework.cli:main']},
    install_requires=requirements,
    license='Other/Proprietary License',
    zip_safe=False,
    keywords='clusterdock',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
