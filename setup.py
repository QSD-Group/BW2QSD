#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:

    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
for license details.
'''

from setuptools import setup

setup(
    name='bw2qsd',
    packages=['bw2qsd'],
    version='0.1.4',
    license='UIUC',
    author='Yalin Li',
    author_email='mailto.yalin.li@gmail.com',
    description='Bridging Brightway2 and QSD packages for LCA',
    long_description=open('README.rst', encoding='utf-8').read(),
    url="https://github.com/QSD-Group/BW2QSD",
    install_requires=[
        'brightway2==2.4.2',
        'beautifulsoup4',
        'py7zr',
    ],
    package_data=
        {'bw2qsd': [
            'eidl/*',
        ]},
    platforms=['Windows', 'Mac', 'Linux'],
    classifiers=[
        'License :: OSI Approved :: University of Illinois/NCSA Open Source License',
        'Environment :: Console',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=[
        'quantitative sustainable design',
        'Brightway2',
        'life cycle assessment',
        'database importer'
    ],
)
