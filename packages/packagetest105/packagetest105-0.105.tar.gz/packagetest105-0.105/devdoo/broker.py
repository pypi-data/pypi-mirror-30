#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Broker:
    def __init__(self, id, name):
        self._ready = False
        self.id = id
        self.name = name

    def ready(self):
        return self._ready
