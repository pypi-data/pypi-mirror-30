#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import moustache_fusion

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


setup(
    name='Moustache-fusion.beta',
    version=moustache_fusion.__version__,
    python_requires='>=3',
    packages=find_packages(),
    author="Libriciel SCOP",
    author_email="hackathon@libriciel.coop",
    description="Module post-Moustache pour fusion d'annexes PDF dans PDF principal",
    long_description=long_description,
    install_requires=[
        'flask',
        'PyPDF2',
        'reportlab'
    ],
    include_package_data=True,
    url='https://gitlab.libriciel.fr/libriciel/outils/skittlespy',
    entry_points={
        'console_scripts': [
            'moustache_fusion = moustache_fusion:launch'
        ],
    },
    license="CeCILL v2",
)
