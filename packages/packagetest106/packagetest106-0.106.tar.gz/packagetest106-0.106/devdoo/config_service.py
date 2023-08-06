#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config


class ConfigService(Config):
    def __init__(self, params, status):
        super(ConfigService, self).__init__(params, status)
