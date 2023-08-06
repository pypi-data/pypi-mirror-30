# -*- coding: utf-8 -*-
# Copyright (c) 2004-2018 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), April 2014
"""
This nmodule is here only to ensure that all PCSE modules can import internally from .traitlets
while this module loads the actual traitlets modules from the correct location.

Currently an adapted version of the traitlets package is used 'traitlets_pcse' which is installed
directly from a github repository.
"""
from traitlets_pcse import *

