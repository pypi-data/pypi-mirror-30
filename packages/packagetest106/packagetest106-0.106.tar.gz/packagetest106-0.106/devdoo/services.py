#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from convert import Convert
from config_database import ConfigDatabase
from config_service import ConfigService
from console import Console



class Services:
    def __init__(self, services, status):
        self.status = status
        self.console = Console()
        self.__services = dict()

        print "SERVICES----->>>", services

        self.__init(services)

    # --------------------------------
    # __init
    # --------------------------------
    def __init(self, list_ids):
        # Recupera a lista de identificadores de serviços que o broker precisa executar
        # Verifica se a lista de identificadores de serviços é válida
        if self.__has_services(list_ids):
            # Vai buscar no servidor console as configurações de cada serviço
            for service_id in list_ids:
                # Recupera a lista de configuração dos serviços que o broker precisa executar
                console_params = self.console.load_config(service_id, self.status)

                service = None
                if console_params.ready():
                    # Verifica o tipo de serviço
                    if console_params.type  == "devdoo-service":
                        # Cria o config do tipo do serviço especificado
                        service = ConfigService(console_params, self.status)
                    # caso contrário verifica se o tipo de serviço é válido e do tipo especificado
                    elif console_params.type  == "devdoo-database":
                        # Cria o config do segunda opção de tipo do serviço
                        service = ConfigDatabase(console_params, self.status)

                # Verifica se a configuração é válida
                if (service is not None) and service.ready():
                    self.status.show("REGISTER_SERVICE", [service.id])
                    # Registra o serviço no stack de serviços
                    self.__services[service.id] = service
                else:
                    self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", service_id])

    def find(self, service_id):
        print "service_id", service_id, self.__services.keys()
        if service_id in self.__services.keys():
            return self.__services[service_id]
        self.status.error("INVALID_SERVICE", None, ["Serviço não configurado", service_id])
        return None

    def ready(self):
        # Retorna status indicando se houve algum erro no processo de configuração dos serviços e se existe serviços para ser executado
        return self.status.ready() and (len(self.__services.keys()) > 0)

    # --------------------------------
    # __has_services
    # --------------------------------
    def __has_services(self, list_ids):
        error = False
        if (type(list_ids) == list) and (len(list_ids) > 0):
            for item in list_ids:
                if not re.match("^[0-9a-f]{24}$", Convert.to_str(item)):
                    error = True
        if error is True:
            self.status.error("INVALID_SERVICE", None, ["Lista de Servicos nao valida", list_ids])

        return self.status.ready()

