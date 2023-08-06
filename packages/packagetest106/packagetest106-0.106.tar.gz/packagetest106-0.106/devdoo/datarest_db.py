#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from bson.json_util import dumps
from convert import Convert
from pack import Pack


# TODO:: Implementar checksum no docuemntos para insert e update
# TODO:: Melhorar formato de dados retornados ao cliente
# TODO:: Verificar se os dados para serem enviados ao cliente estão dentro das especificações esperadas
# TODO:: Implementar sistema de gestão de consumo, analitico, histórico e log
# TODO:: Verificar todas as entradas de dados, confirmar tipagem esperada
# TODO:: Implementar configurações do info de documento
# TODO:: Melhorar mensagem de retorno em caso de falha

# Registra o checksum do documento
# self.__checksum = Convert.to_checksum(data)
class DataRestDB:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, message, status):
        self.status = status
        self.pack = Pack(message)
        self.pack.decode(status)

        if self.pack.ready():
            self.__action = None
            self.__collection = None
            self.__data = dict()
            self.__default_limit = 100
            self.__fields = []
            self.__filter = None
            self.__info = dict()
            self.__limit = 0
            self.__max_limit = 200
            self.__message_send = dict()
            self.__method = None
            self.__offset = 0
            self.__regex = None
            self.__result_type = None
            self.__search = None
            self.__sort = None
            self.__token = None

            self.decode_database()

    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        return self.pack.action

    # --------------------------------
    # collection
    # --------------------------------
    def collection(self):
        return self.__collection

    # --------------------------------
    # changed_time
    # --------------------------------
    def changed_time(self):
        self.__changed_time = Convert.to_str(datetime.datetime.utcnow())

    # --------------------------------
    # created_time
    # --------------------------------
    def created_time(self):
        self.__created_time = Convert.to_str(datetime.datetime.utcnow())

    # --------------------------------
    # data
    # --------------------------------
    def data(self):
        return self.__data

    # --------------------------------
    # database
    # --------------------------------
    def database(self):
        return self.pack.database

    # --------------------------------
    # decode
    # --------------------------------
    def decode_database(self):
        body = self.pack.body
        self.__data = body["data"]
        self.__collection = body["collection"]
        self.__fields = body["fields"]
        self.__filter = body["filter"]
        self.__limit = int(body["limit"])
        self.__method = body["method"]
        self.__offset = int(body["offset"])
        self.__regex = body["regex"]
        self.__result_type = body["result_type"]
        self.__search = body["search"]
        self.__sort = body["sort"]


    # --------------------------------
    # fields
    # --------------------------------
    def fields(self):
        return self.__fields

    # --------------------------------
    # filter
    # --------------------------------
    def filter(self):
        return self.__filter

    # --------------------------------
    # info
    # --------------------------------
    def info(self):
        return {
            "owner": {
                "id": self.__token,
                "last_id": self.__token
            }
        }

    # --------------------------------
    # limit
    # --------------------------------
    def limit(self):
        return self.__limit

    # --------------------------------
    # offset
    # --------------------------------
    def offset(self):
        return self.__offset

    # --------------------------------
    # result
    # --------------------------------

    def result(self, message):
        message["elapsed_time"] = {"response": "17.000", "server": "7.000"}
        message["method"] = self.__method
        if self.status.has_error():
            message["errors"] = self.status.to_list()
        self.__message_send = message

    # --------------------------------
    # result_type
    # --------------------------------
    def result_type(self):
        return self.__result_type

    # --------------------------------
    # send
    # --------------------------------

    # Registrar no stack de log
    # Registrar no stack de analytic
    # Registrar no stack de error
    # Registrar no stack de history
    # self.analyric.add(dict())
    def send_result(self):
        message = {
            "action": self.pack.action,
            "active_port": self.pack.active_port,
            "alerts": {
                "error": self.status.to_list(),
                "log": None,
                "warn": None,
                "info": None,
            },
            "app_id": self.pack.app_id,
            "api_key": self.pack.api_key,
            "body": self.__message_send,
            "id": self.pack.id,
            "lenght_in": self.pack.lenght_in,
            "lenght_out": None,
            "service": self.pack.service,
            "service_id": self.pack.service_id,
            "database_id": None,
            "open": False,
            "source": self.pack.source,
            "success": True,
            "time": {
                "time_start": None,
                "service": None,
                "database": None
            }
        }
        return dumps(message)

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        # Montar mensagem que será enviada para o serviço de base de dados
        message = {
            "action": self.pack.action,
            "active_port": self.pack.active_port,
            "alerts": {
                "error": self.status.to_list(),
                "log": None,
                "warn": None,
                "info": None,
            },
            "app_id": self.pack.app_id,
            "api_key": self.pack.api_key,
            "body": self.__message_send,
            "id": self.pack.id,
            "lenght_in": self.pack.lenght_in,
            "lenght_out": None,
            "service": self.pack.service,
            "service_id": self.pack.service_id,
            "database_id": None,
            "open": False,
            "source": self.pack.source,
            "success": False,
            "time": {
                "time_start": None,
                "service": None,
                "database": None
            }
        }
        return dumps(message)

    # --------------------------------
    # sort
    # --------------------------------
    def sort(self):
        return self.__sort
