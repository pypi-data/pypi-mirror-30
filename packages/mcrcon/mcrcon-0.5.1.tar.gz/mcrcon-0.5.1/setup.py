#!/usr/bin/env python

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='mcrcon',
    version='0.5.1',
    description='A client for handling Remote Commands (RCON) to a '
                'Minecraft server.',
    long_description=long_description,
    url='https://github.com/uncaught-exceptions/mcrcon',
    author='Adrian Turjak',
    author_email='minecraft@uncaught-exceptions.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='openstack keystone users tasks registration workflow',
    py_modules=['mcrcon']
)
