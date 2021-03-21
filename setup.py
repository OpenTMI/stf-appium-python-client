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
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Software Development :: Testing
""".strip().splitlines()

setup(
    name='stf_appium_client',
    use_scm_version=True,
    packages=find_packages(exclude=['test']),  # Required
    url='https://github.com/opentmi/stf_appium_client',
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
        "pyswagger",
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
        'dev': ['wheel', 'coverage', 'coveralls', 'mock', 'pylint', 'nose', 'pyinstaller']
    },
    keywords="OpenSTF appium robot-framework lockable resource android",
    python_requires=">=3.6",
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/opentmi/stf_appium_client',
        'Source': 'https://github.com/opentmi/stf_appium_client',
    }
)
