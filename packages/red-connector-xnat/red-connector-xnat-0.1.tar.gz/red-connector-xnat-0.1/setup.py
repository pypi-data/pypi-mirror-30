#!/usr/bin/env python3

from setuptools import setup

setup(
    name='red-connector-xnat',
    version='0.1',
    description='Red Connector XNAT.',
    author='Christoph Jansen',
    author_email='Christoph.Jansen@htw-berlin.de',
    url='https://github.com/curious-containers/red-connector-xnat',
    packages=[
        'red_connector_xnat'
    ],
    license='AGPL-3.0',
    platforms=['any'],
    install_requires=[
        'requests',
        'jsonschema'
    ]
)
