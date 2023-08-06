#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from convert import Convert

class ServiceSocket:
    def __init__(self, pack, service):
        self.__ready = False
        self.backend = None
        self.message = pack.to_string()

        if (service is not None) and service.ready():
            # Cria contexto ZMQ
            context = zmq.Context()

            #service.show()

            # Abre portas para os Serviços no backend
            self.backend = context.socket(zmq.DEALER)

            print "broker_rest_backend---->>>>>", service.endpoints["broker_rest_backend"]

            self.backend.bind(service.endpoints["broker_rest_backend"])
            self.__ready = True

    def ready(self):
        return self.__ready