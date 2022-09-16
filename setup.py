#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2021 by Jussi Vatjus-Anttila
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup, find_packages


CLASSIFIERS = """
Development Status :: 3 - Alpha
Topic :: Software Development :: Testing
Operating System :: OS Independent
License :: OSI Approved :: Apache Software License
Operating System :: POSIX
Operating System :: Microsoft :: Windows
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Topic :: Software Development :: Testing
""".strip().splitlines()

setup(
    name='stf_appium_client',
    use_scm_version=True,
    packages=find_packages(exclude=['test']),  # Required
    url='https://github.com/OpenTMI/stf-appium-python-client',
    license='MIT',
    author='Jussi Vatjus-Anttila',
    author_email='jussiva@gmail.com',
    description='STF client with appium',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    classifiers=CLASSIFIERS,
    setup_requires=["setuptools_scm"],
    install_requires=[
        "Appium-Python-Client",
        "stf-client==0.1.0",
        "pydash",
        "easyprocess",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'stf = stf_appium_client.cli:main'
        ]
    },
    extras_require={  # Optional
        'dev': ['wheel', 'mock', 'pylint', 'pytest', 'pytest-cov', 'pytest-mock', 'pyinstaller', 'coveralls']
    },
    keywords="OpenSTF appium robot-framework lockable resource android",
    python_requires=">=3.7",
    project_urls={  # Optionaly
        'Bug Reports': 'https://github.com/OpenTMI/stf-appium-python-client/issues',
        'Source': 'https://github.com/OpenTMI/stf-appium-python-client',
    }
)
