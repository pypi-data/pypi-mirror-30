#!/usr/bin/env python
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()

with open(os.path.join(here, 'tempcase', 'version.py')) as f:
    exec(f.read())

setup(
    name='tempcase',
    version=__version__,
    packages=find_packages(exclude=('tests',)),
    url='https://github.com/clbarnes/tempcase',
    license='MIT',
    install_requires=['backports.tempfile>=1.0; python_version < "3.4"'],
    author='Chris L Barnes',
    author_email='barnesc@janelia.hhmi.org',
    description='Utilities for handling python test cases with temporary directories and files, '
                'for people using `pyunit`/`unittest`.',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='test unittest pyunit tmp temp',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*'
)
