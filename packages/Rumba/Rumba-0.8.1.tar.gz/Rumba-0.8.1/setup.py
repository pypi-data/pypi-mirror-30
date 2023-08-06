#!/usr/bin/env python

import setuptools

_locals = {}
with open('rumba/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']

setuptools.setup(
    name='Rumba',
    version=version,
    url='https://gitlab.com/arcfire/rumba',
    keywords='rina measurement testbed',
    author='Sander Vrijders',
    author_email='sander.vrijders@ugent.be',
    license='LGPL',
    description='Rumba measurement framework for RINA',
    packages=[
        'rumba',
        'rumba.testbeds',
        'rumba.prototypes',
        'rumba.executors',
        'rumba.elements'
    ],
    install_requires=[
        'paramiko',
        'docker',
        'repoze.lru; python_version<"3.2"',
        'contextlib2; python_version<"3.0"',
        'enum34; python_version<"3.0"'
    ],
    extras_require={'NumpyAcceleration': ['numpy']},
    scripts=['tools/rumba-access']
)
