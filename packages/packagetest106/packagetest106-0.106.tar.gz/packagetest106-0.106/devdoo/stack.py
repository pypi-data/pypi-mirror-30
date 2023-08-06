#!/usr/bin/env python
# -*- coding: utf-8 -*-

from service_socket import ServiceSocket


class Stack:
    def __init__(self):

        self.__sockets = dict()

    # --------------------------------
    # find_socket
    # --------------------------------
    # TODO:: Mudar identificador de serviço de active port para id
    def socket(self, pack, service, status):
        socket = None
        if pack.is_valid() and (pack.id in self.__sockets.keys()):
            socket = self.__sockets[pack.id]
        elif pack.is_valid():
            socket = ServiceSocket(pack, service)
            if socket.ready():
                self.__sockets[pack.id] = socket
        else:
            socket = ServiceSocket(pack, None)

        if socket.ready() is not True:
            status.error("INVALID_SERVICE", None, ["Servico nao disponivel no servidor BROKER", pack.service_id])

        return socket

