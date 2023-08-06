#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from check import Check
from convert import Convert
from status import Status
from bson.json_util import dumps
from pprint import pprint


# TODO: Refatorar classe completa Pack
# TODO: Alterar o nome da classe para pack
class Pack:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, message, status):
        self.__ready = False
        self.message = message
        self.status = status

        self.action = None  # Ação a ser executada (get, post, put, delete?)
        self.active_port = None  # Identificador da porta do serviço ativo
        self.alerts = {
            "error": None,  # Mensagens de erro para o desenvolvedor corrigir a aplicação ou apresentar ao usuário
            "log": None,  # Mensagens de log para o desenvolvedor corrigir sua aplicação
            "warn": None,  # Mensagens de warn para o desenvolvedor apresentar ao usuário
            "info": None,  # Mensagens de info para o desenvolvedor apresentar ao usuário
        }
        self.app_id = None  # Id da aplicação
        self.api_key = None  # Chave de acesso da api
        self.body = dict()  # Todos os dados que precisam ser transportados entre os serviços
        self.id = None  # Id da conexão, gerado no REST
        self.lenght_in = 0  # Tamanho do pacote de entrada
        self.lenght_out = 0  # Tamanho do pacote de saída
        self.service = None  # Identificador do serviço
        self.service_id = None  # Id do serviço a ser executado
        self.database_id = None  # Id numérico do base de dados
        self.open = True  # Indica se a conexão está aberta/fechada 0=close|1=open
        self.source = None  # Uri da api
        self.success = False  # Status boleano indicando sucesso ou falha na operação
        self.time = {
            "time_start": 0,  # Momento de inicio da conexão no REST
            "service": 0,  # Momento de inicio da operação no serviço
            "database": 0  # Momento de inicio da operação do serviço de banco
        }

        self.__decode()

    # --------------------------------
    # active_service
    # --------------------------------
    def active_service(self, database_id):
        self.database_id = database_id
        self.active_port = database_id

    # --------------------------------
    # decode
    # --------------------------------
    def __decode(self):

        # Verifica se a mensagem é do tipo lista e tem mais de três elementos e o terceiro elemento seja do tipo string
        if (type(self.message) == list) and (len(self.message) >= 3) and Check.is_string(self.message[2]):
            # Converte o terceiro elemento da lista em object (dic)
            pack = Convert.to_object(self.message[2])

            # Verifica se é um objeto válido
            if Check.is_object(pack):
                #self.active_port = pack["active_port"] # TODO:: Remover active port
                self.action = pack["action"]
                self.alerts = {
                    "error": pack["alerts"]["error"],
                    "log": pack["alerts"]["log"],
                    "warn": pack["alerts"]["warn"],
                    "info": pack["alerts"]["info"]
                }
                self.app_id = pack["app_id"]
                self.api_key = pack["api_key"]
                self.body = pack["body"]
                self.id = pack["id"]
                self.lenght_in = sys.getsizeof(self.message)
                self.lenght_out = pack["lenght_out"]
                self.service = Convert.to_str(pack["service"])
                self.service_id = Convert.to_str(pack["service_id"])
                self.database_id = Convert.to_str(pack["database_id"])
                self.open = pack["open"]
                self.source = pack["source"]
                self.success = pack["success"]
                self.time = {
                    "time_start": pack["time"]["time_start"],
                    "service": pack["time"]["service"],
                    "database": pack["time"]["database"]
                }
                self.database = "db" + self.database_id + self.service
                self.token = "xvz1evFS4wEEPTGEFPHBog:L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg"
                self.__ready = True
            else:
                self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])
        else:
            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])

    # --------------------------------
    # is_valid
    # --------------------------------
    def is_valid(self):
        self.__check_pack()
        return self.ready()

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.__ready and self.status.ready()

    # --------------------------------
    # to_string
    # --------------------------------
    def to_string(self):
        return dumps(self.pack)

    # --------------------------------
    # __check_pack
    # --------------------------------
    def __check_pack(self):
        # Verifica se mensagem é string
        if (type(self.message) == list) and len(self.message) >= 3:
            # Converte a mensagem recebida do servidor rest para objeto
            self.pack = Convert.to_object(self.message[2])

            # Verifica se o pacote de mensagem é do tipo objeto válido
            if Check.is_object(self.pack):
                # Verifica se o pacote de mensagem é válido
                self.__ready = self.__check_params(self.pack)

                if self.__ready is not True:
                    self.status.error("INVALID_PACKAGE", None, ["Pacote de comunicacao invalido"])
                    self.pack["alerts"] = {"error": self.status.to_list(), "log": None, "warn": None, "info": None}
                    self.pack["success"] = False
                    self.pack["status"] = 0

    # --------------------------------
    # __check_params
    # --------------------------------
    # Verifica se o pacote de comunicação é válido
    def __check_params(self, pack):
        errors = []

        # Verifica se no pacote existe o identificador do serviço
        if "action" not in pack.keys():
            errors.append("ACTION")

        if "alerts" not in pack.keys():
            errors.append("ALERTS")

        if "body" not in pack.keys():
            errors.append("BODY")

        if "lenght_in" not in pack.keys():
            errors.append("LENGHT_IN")

        if "lenght_out" not in pack.keys():
            errors.append("LENGHT_OUT")

        if "open" not in pack.keys():
            errors.append("OPEN")

        if "source" not in pack.keys():
            errors.append("SOURCE")

        if "success" not in pack.keys():
            errors.append("SUCCESS")

        if "time" not in pack.keys():
            errors.append("TIME")

        if "api_key" not in pack.keys():
            errors.append("API_KEY")

        if "id" not in pack.keys():
            errors.append("ID")

        if "service" not in pack.keys():
            errors.append("SERVICE")

        if "service_id" not in pack.keys():
            errors.append("SERVICE ID")

        if len(errors) > 0:
            self.status.error("INVALID_PACKAGE_PARAMS", None, ["Pacote de comunicacao nao tem:", (",".join(errors))])
            return False
        return True

    def show(self):
        pprint(self.__dict__)