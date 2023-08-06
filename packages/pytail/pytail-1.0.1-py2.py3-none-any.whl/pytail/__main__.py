#!/usr/bin/env python
"""Tail files via TCP"""
import logging
from . import config, pytail

CFG = config.Config()

logging.basicConfig(level=CFG.get('loglevel'), format=CFG.get('logformat'),
                    filename=CFG.get('logfile'))
logging.captureWarnings(True)

pytail.Server().listen()
