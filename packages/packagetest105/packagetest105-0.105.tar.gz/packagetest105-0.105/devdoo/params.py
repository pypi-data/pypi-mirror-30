#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint


class Params:
    def __init__(self, id, config, status):
        self.status = status
        self.id = None
        self.database = None
        self.mongodb = None
        self.collections = None
        self.actions = None
        self.brokers = None
        self.endpoint = None
        self.endpoints = None
        self.name = None
        self.type = None
        self.services = None

        self.__init(id, config)

    def ready(self):
        return self.status.ready()

    def __init(self, id, config):
        if (config is not None) and (type(config) == dict):
            for field in config:
                self.__dict__[field] = config[field]
            self._read = True
        else:
            self.status.error("FAIL_LOAD_FILE_CONFIG", None, ["Arquivo de configuracao invalido", id])

    def __setitem__(self, field, value):
        self.field = value

    def show(self):
        pprint(self.__dict__)
