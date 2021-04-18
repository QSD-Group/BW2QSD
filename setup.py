#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License. Please refer to
https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
for license details.
'''

from setuptools import setup

setup(
    name='bw2qsd',
    packages=['bw2qsd'],
    version='0.0.9',
    license='UIUC',
    author='Yalin Li',
    author_email='zoe.yalin.li@gmail.com',
    description='Bridging Brightway2 and QSD packages for LCA',
    long_description=open('README.rst').read(),
    url="https://github.com/QSD-Group/BW2QSD",
    install_requires=['eidl', 'xlrd<=1.2.0'],
    package_data=
        {'bw2qsd': [
                    'sample_output.tsv',
                    'Tutorial.ipynb',
                    ]},
    platforms=['Windows', 'Mac', 'Linux'],
    classifiers=['License :: OSI Approved :: University of Illinois/NCSA Open Source License',
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
                 'Operating System :: MacOS',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'Operating System :: POSIX :: BSD',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 ],
    keywords=['Brightway2', 'quantitative sustainable design', 'life cycle assessment', 'database importer'],
)