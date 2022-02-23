#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is copied from the EcoInventDownLoader (eidl) repository at
https://github.com/haasad/EcoInventDownLoader
with only minor bug fix and modification to be compatible with BW2QSD.

The reason for including this module in BW2QSD rather than adding EcoInventDownLoader
as a dependent package is because EcoInventDownLoader does not have a PyPI release,
and installing it via conda requires the installation of the entire Brightway2 framework
via conda, which has some unfixed bugs, and the use of both pip and conda in installation
could be overwhelming for users.

This module is under dual licenses:

	EcoInventDownLoader (MIT)
	Please refer to https://github.com/haasad/EcoInventDownLoader/blob/master/LICENSE
	for license details.

	BW2QSD (University of Illinois/NCSA)
	Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
'''

from .storage import eidlstorage
from .core import EcoinventDownloader, get_ecoinvent

__all__ = ['EcoinventDownloader', 'get_ecoinvent', 'eidlstorage']