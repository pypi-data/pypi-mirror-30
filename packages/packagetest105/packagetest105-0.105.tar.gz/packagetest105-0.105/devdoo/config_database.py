#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Config


class ConfigDatabase(Config):
    def __init__(self, params, status):
        super(ConfigDatabase, self).__init__(params, status)
