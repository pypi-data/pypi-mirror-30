#!/usr/bin/env python
# -*- coding: utf-8 -*-

from check import Check
from pprint import pprint


class Config(object):
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, params, status):
        self.__ready = False

        self.id = None
        self.database = None
        self.brokers = None
        self.endpoint = None
        self.endpoints = None
        self.name = None
        self.type = None
        self.services = None

        self.status = status

        self.__init(params)

    # --------------------------------
    # __init
    # --------------------------------
    def __init(self, params):

        if params.ready():
            # Identificador do serviço
            self.id = Check.value_string("id", params.id, self.status)
            # Nome do serviço
            self.name = Check.value_string("name", params.name, self.status)
            # Identificador do tipo de serviço (devdoo-broker|devdoo-database|devdoo-service)
            self.type = Check.value_string("type", params.type, self.status)

            if self.type == "devdoo-broker":
                self.services = Check.value_list("services", params.services, self.status)
                self.endpoint = Check.value_string("endpoint", params.endpoint, self.status)

            elif (self.type == "devdoo-service"):
                self.mongodb = Check.value_dict("mongodb", params.database, self.status)
                self.endpoint = Check.value_dict("endpoint", params.database, self.status)
                self.endpoints = Check.value_string("endpoints", params.endpoints, self.status)

            elif (self.type == "devdoo-database"):
                self.mongodb = Check.value_dict("mongodb", params.mongodb, self.status)
                self.collections = Check.value_dict("collections", params.mongodb, self.status)
                self.actions = Check.value_dict("actions", params.mongodb, self.status)

        self.status.show("CONFIG_INIT", [self.type])
        return self.status.ready()

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        if self.status.ready() is False:
            pprint(self.status.to_list())
        return self.status.ready()

    def show(self):
        pprint(self.__dict__)