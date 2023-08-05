# -*- coding: utf-8 -*-
from __future__ import with_statement

from setuptools import setup


version = '1.0.4'


setup(
    name='django-curtail-uuid',
    version=version,
    keywords='django-curtail-uuid',
    description='Curtail UUID Appointed Length',
    long_description=open('README.rst').read(),

    url='https://github.com/Brightcells/django-curtail-uuid',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_curtail_uuid'],
    py_modules=[],
    install_requires=['shortuuid'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
