#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

__version__ = '1.0.0'

try:
    from thumbor_engine_opencv.engine import Engine  # NOQA
except ImportError:
    logging.exception('Could not import thumbor_engine_opencv. Probably due to setup.py installing it.')
