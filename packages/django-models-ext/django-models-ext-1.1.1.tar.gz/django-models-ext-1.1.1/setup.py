# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.1.1'


setup(
    name='django-models-ext',
    version=version,
    keywords='Django Models Ext Extensions',
    description='Django Models Extensions',
    long_description=open('README.rst').read(),

    url='https://github.com/django-xxx/django-models-extensions',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_models_ext'],
    py_modules=[],
    install_requires=['TimeConvert'],

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
