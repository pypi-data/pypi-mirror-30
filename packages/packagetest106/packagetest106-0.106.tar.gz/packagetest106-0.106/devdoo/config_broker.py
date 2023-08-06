#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config


class ConfigBroker(Config):
    def __init__(self, params, status):
        super(ConfigBroker, self).__init__(params, status)
