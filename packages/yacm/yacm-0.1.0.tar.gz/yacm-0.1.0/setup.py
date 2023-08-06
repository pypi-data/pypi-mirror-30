#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['PyYAML>=3.10']

setup_requirements = []

test_requirements = ['pytest', ]

setup(
    author="Florian Ludwig",
    author_email='f.ludwig@greyrook.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="yet another config module",
    entry_points={
        'console_scripts': [
            'yacm=yacm.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='yacm',
    name='yacm',
    packages=find_packages(include=['yacm']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/FlorianLudwig/yacm',
    version='0.1.0',
    zip_safe=False,
)
