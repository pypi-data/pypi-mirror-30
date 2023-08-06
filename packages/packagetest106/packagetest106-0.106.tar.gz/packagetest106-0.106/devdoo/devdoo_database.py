#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from devdoo_base import DevdooBase
from convert import Convert
from service_db import ServiceDB
from config_database import ConfigDatabase

# TODO:: Implementar autoconfiguração do serviço, comunicação com console admin
# TODO:: Enviar para o servidor console a informação de falha de configuração
class DevdooDatabase(DevdooBase):
    # --------------------------------
    # Error
    # --------------------------------
    # TODO:: Remover classe de error
    class Error(Exception):
        pass

    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        super(DevdooDatabase, self).__init__()

        # Serviço a ser executado
        self.service = None
        self.config = self.init_config(ConfigDatabase)

        if self.config.ready():
            self.status.show("SERVICE_ID", [self.config.id])
            self.__init()
        else:
            self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", self.config.id])
            self.status.to_print()

    # --------------------------------
    # __init
    # --------------------------------
    def __init(self):
        if self.__is_start_services() is True:
            # Cria contexto ZMQ
            context = zmq.Context()

            # Adaptador de conexão
            self.socket_frontend = context.socket(zmq.REP)
            self.socket_frontend.connect(self.config.endpoint["broker_database"])

            self.status.show("SERVICE_INIT", [self.config.type])
            self.run()
        else:
            self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", self.config.id])
            self.status.to_print()

    # --------------------------------
    # __is_start_services
    # --------------------------------
    def __is_start_services(self):
        # Vai até o servidor console buscar informações de configurações do serviços assoaciadas eo identificador do serviço
        # Recupera o identificador do serviço 'devdoo-broker' no arquivo yml
        self.config.console_load_pre_config("devdoo-database")

        # Retorna status indicando se houve algum erro no processo de configuração do serviço
        return self.status.ready()

    # --------------------------------
    # operation
    # --------------------------------
    # Executa a ação do Serviço
    #
    # TODO:: Implementar controle ready antes de seguir adiante
    def operation(self):
        # Recebe do mensagem do servidor cliente
        self.process(self.socket_frontend.recv())

        # Processa a operacao e envia mensage de retorno para o cliente
        self.socket_frontend.send(self.service.send())

    # --------------------------------
    # process
    # --------------------------------
    # Inicia o Serviço de banco
    #
    def process(self, message):
        self.service = ServiceDB(message, self.config)

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #
    # TODO:: Implementar ping de verificação de disponibilidade do serviço
    def run(self):
        while True:
            try:
                self.operation()
            except DevdooDatabase.Error:
                pass
                # except Exception as inst:
                #    print "API_DB::RUN::ERROR", inst.args
