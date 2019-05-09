#!/usr/bin/python
# -*- coding: utf-8 -*-

from .logger import myLogger
log = myLogger(debug=True)

__title__ = 'CameraSequencer'
__author__ = 'Christopher DeVito'
__email__ = 'Chris.Devito@methodstudios.com'
__url__ = ''
__version__ = '0.0.1'
__license__ = ''
__description__ = '''A Maya camera sequencer.'''

from .utils import *
