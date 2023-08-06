#!/usr/bin/env python

from __future__ import absolute_import

from setuptools import setup


with open('sphinxcontrib/_version.py') as f:
    contents = f.read()
    exec(contents)  # defines __version__

with open('README.rst') as f:
    docstr = f.read()

setup(
    name='sphinxcontrib-xbr',
    version=__version__,  # noqa
    author='Crossbar.io Technologies GmbH',
    author_email='support@crossbario.com',
    description='XBR IDL extension for Sphinx',
    long_description=docstr,
    url='https://crossbario.com',
    platforms=('Any'),
    include_package_data=True,
    data_files=[
        ('.', ['LICENSE', 'README.rst', 'sphinxcontrib/_version.py'])
    ],
    zip_safe=True,
    license='BSD License',
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development :: Documentation',
    ],
    keywords='sphinx wamp xbr idl generator documentation crossbar autobahn'
)
