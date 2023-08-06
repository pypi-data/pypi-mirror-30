#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from params import Params

HOST_IP = socket.gethostbyname(socket.gethostname())
ENDPOINT_BROKER_REST = 'tcp://localhost:23210'
ENDPOINT_BROKER_DATABASE = 'tcp://localhost:43210'  # esse é o ip e a porta onde o serviço de banco conecta no backend do broker de database
MONGO_IP = 'localhost'

# Verifica se esta executando no Docker ou On-line
if HOST_IP[:3] == '10.':
    ENDPOINT_BROKER_REST = 'tcp://10.10.0.1:23210'
    ENDPOINT_BROKER_DATABASE = 'tcp://10.30.0.1:43210'
    MONGO_IP = '10.50.0.1'

print 'HOST IP:', HOST_IP
print 'ENDPOINT_BROKER_REST:', ENDPOINT_BROKER_REST
print 'ENDPOINT_BROKER_DATABASE:', ENDPOINT_BROKER_DATABASE
print 'MONGO_IP:', MONGO_IP

server_console = {
    # primeiro broker (rest)
    "5abe46fd83566949ecc10121": {
        "id": "5abe46fd83566949ecc10121",
        "name": "Broker-RS90",
        "type": "devdoo-broker",
        "endpoint_frontend": "tcp://*:10121",  # entrada do broker rest ??  confere  sim
        "services":
            ["5abe46fd83566949ecc23210"]
    },

    # segundo broker (database)
    "5abe46fd83566949ecc30188": {
        "id": "5abe46fd83566949ecc30188",
        "name": "Broker-DB45",
        "type": "devdoo-broker",
        "endpoint_frontend": "tcp://*:30188",  # entrada do broker service isso confere? ??
        "services": ["5abe46fd83566949ecc23210"]
    },

    # BROKER REST:
    #   frontend - tcp://*:10121  (recebe conexão do rest)
    #   backends - [tcp://*:23210]  (recebe conexão dos serviços api)
    # SERVICE API:
    #   conecta em  tcp://localhost:23210 (conecta no broker rest)
    #               tpc://localhost:30188 (conecta no broker service)
    # BROKER SERVICE:
    #   frontend - tcp://*:30188   (recebe conexão dos serviços api)
    #   backends - [tpc://*:43210]  (recebe conexão dos serviços database)
    # SERVICE DB:
    #   conecta em  tcp://localhost:43210 (conecta no broker service)

    # serviço API
    "5abe46fd83566949ecc23210":
        {
            "id": "5abe46fd83566949ecc23210",
            "name": "log",
            "type": "devdoo-service",
            "brokers": {
                "frontend": "tcp://localhost:10121", # rest conecta ao primeiro broker
                "backends":["tcp://*:23210"] # Lista de brokers para os serviços conectarem
            },
            "endpoint": "tcp://localhost:23210",  # serviço conecta ao broker rest
            "database": {
                "mongodb": {
                    "ip": MONGO_IP,
                    "port": 27017,
                },
                "brokers": {
                    "frontend": "tcp://localhost:30188", # serviço conecta ao segundo broker
                    "backends": ["tcp://*:43210"] # Lista de brokers para os serviços de banco conectarem
                },
                "endpoint": "tcp://localhost:43210", # serviço de banco conecta ao broker de banco
                "collections": {
                    "messages": {
                        "name": "messages",  # nome da coleção
                        "id": "6355814a9f68d0ad190c4d54",  # id da coleção
                        "schemes": {  # detalhes de configuração dos campos da coleção (schema)
                            "type_array": {"id": "6355814a9f68d0ad190c1001", "field": "type_array", "type": "array", "info": "Array",
                                           "version": "1.0", "public": True},
                            "type_boolean": {"id": "6355814a9f68d0ad190c1002", "field": "type_boolean", "type": "boolean", "info": "Boolean",
                                             "version": "1.0", "public": True},
                            "type_number": {"id": "6355814a9f68d0ad190c1003", "field": "type_number", "type": "number", "info": "Number",
                                            "version": "1.0", "min_value": "100", "max_value": "3000", "required": "true", "public": True},
                            "type_decimal": {"id": "6355814a9f68d0ad190c1004", "field": "type_decimal", "type": "decimal", "info": "Number Decimal",
                                             "version": "1.0", "public": True},
                            "type_object": {"id": "6355814a9f68d0ad190c1005", "field": "type_object", "type": "object", "info": "Object",
                                            "version": "1.0", "public": False},
                            "type_timestamp": {"id": "6355814a9f68d0ad190c1006", "field": "type_timestamp", "type": "timestamp", "info": "Timestamp",
                                               "version": "1.0", "public": True},
                            "type_objectid": {"id": "6355814a9f68d0ad190c1007", "field": "type_objectid", "type": "object_id", "info": "ObjectId",
                                              "version": "1.0", "public": True},
                            "type_enum": {"id": "6355814a9f68d0ad190c1008", "field": "type_enum", "type": "enum", "info": "Enum", "version": "1.0",
                                          "enum": ["M", "F", "34"], "public": False},
                            "type_string": {"id": "6355814a9f68d0ad190c1009", "field": "type_string", "type": "string", "info": "String",
                                            "version": "1.0", "public": False},
                            "type_date": {"id": "6355814a9f68d0ad190c1010", "field": "type_date", "type": "date", "info": "Date", "version": "1.0",
                                          "public": False},
                            "code": {"id": "6355814a9f68d0ad190c1011", "field": "code", "type": "number", "info": "Código do erro", "version": "1.0",
                                     "public": True},
                            "script": {"id": "6355814a9f68d0ad190c1012", "field": "script", "type": "object", "info": "Nome do script",
                                       "version": "1.0", "public": False},
                            "container": {"id": "6355814a9f68d0ad190c1013", "field": "container", "type": "object", "info": "ID do container",
                                          "version": "1.0", "public": True},
                            "instance": {"id": "6355814a9f68d0ad190c1014", "field": "instance", "type": "object", "info": "ID da instância",
                                         "version": "1.0", "public": True},
                            "created_at": {"id": "6355814a9f68d0ad190c1015", "field": "created_at", "type": "date", "info": "Horário da ocorrência",
                                           "version": "1.0", "public": False},
                            "user": {"id": "6355814a9f68d0ad190c1016", "field": "user", "type": "object", "info": "Código do usuário",
                                     "version": "1.0", "public": True},
                            "service": {"id": "6355814a9f68d0ad190c1017", "field": "service", "type": "object", "info": "Código do serviço",
                                        "version": "1.0", "public": False},
                            "type": {"id": "6355814a9f68d0ad190c1018", "field": "type", "type": "string", "info": "Tipo do (error|warn|info|log)",
                                     "version": "1.0", "public": True},
                            "message": {"id": "6355814a9f68d0ad190c1019", "field": "message", "type": "string", "info": "Detalhes extras",
                                        "version": "1.0", "public": False}
                        }
                    }
                },
                "actions": {
                    "get": {
                        # --------------------------------
                        # messages
                        # --------------------------------
                        "/1.0/devdoo/log/system/messages": {
                            "fields": {
                                "default": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number",
                                    "type_decimal",
                                    "type_object",
                                    "type_timestamp",
                                    "type_objectid",
                                    "type_enum",
                                    "type_string",
                                    "type_date",
                                    "type_bola",
                                    "code",
                                    "script",
                                    "container",
                                    "created_at",
                                    "user",
                                    "service",
                                    "type",
                                    "message"
                                ],
                                "public": []
                            },
                            "scheme": dict(),
                            "action": "find",
                            "collection": "messages",
                            "type": "list",
                            "max_limit": 100
                        }
                    },
                    "put": {
                        # --------------------------------
                        # mensagens
                        # --------------------------------
                        "/1.0/devdoo/log/system/edit-message": {

                            "fields": {
                                "default": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number",
                                    "type_decimal",
                                    "type_object",
                                    "type_timestamp",
                                    "type_objectid",
                                    "type_enum",
                                    "type_string",
                                    "type_date",
                                    "type_bola",
                                    "code",
                                    "script",
                                    "container",
                                    "created_at",
                                    "user",
                                    "service",
                                    "type",
                                    "message"
                                ],
                                "public": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number",
                                    "type_decimal",
                                    "type_object",
                                    "type_timestamp",
                                    "type_objectid",
                                    "type_enum",
                                    "type_string",
                                    "type_date",
                                    "type_bola",
                                    "code",
                                    "script",
                                    "container",
                                    "created_at",
                                    "user",
                                    "service",
                                    "type",
                                    "message"
                                ]
                            },
                            "scheme": {
                                "$set": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number",
                                    "type_decimal",
                                    "type_object",
                                    "type_timestamp",
                                    "type_objectid",
                                    "type_enum",
                                    "type_string",
                                    "type_date",
                                    # "type_bola", TODO:: Verificar problema com campos que não existem na coleção
                                    "code",
                                    "script",
                                    "container",
                                    "created_at",
                                    "user",
                                    "service",
                                    "type",
                                    "message"
                                ]
                            },
                            "action": "update",
                            "collection": "messages",
                            "type": "item",
                            "max_limit": 1
                        }
                    },
                    "post": {
                        # --------------------------------
                        # mensagens
                        # --------------------------------
                        "/1.0/devdoo/log/system/add-message": {

                            "fields": {
                                "default": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number",
                                    "type_decimal",
                                    "type_object",
                                    "type_timestamp",
                                    "type_objectid",
                                    "type_enum",
                                    "type_string",
                                    "type_date",
                                    "type_bola",
                                    "code",
                                    "script",
                                    "container",
                                    "created_at",
                                    "user",
                                    "service",
                                    "type",
                                    "message"
                                ],
                                "public": []
                            },
                            "scheme": dict(),
                            "action": "insert",  # TODO: Mudar o nome da operação de database para operation
                            "collection": "messages",
                            "type": "item",
                            "max_limit": 100
                        }

                    },
                    "delete": {
                        # --------------------------------
                        # mensagens
                        # --------------------------------
                        "/1.0/devdoo/log/system/remove-message": {

                            "fields": {
                                "default": [],
                                "public": []
                            },
                            "scheme": dict(),
                            "collection": "messages",
                            "action": "remove",
                            "type": "list",
                            "max_limit": 100
                        }
                    }
                }
            }

        }

}


# TODO:: Mudar estutura de configuração de scheme e actions
class Console:
    @staticmethod
    def load_config(id, status):
        config = server_console[id]
        if config is not None:
            return Params(id, config, status)
        else:
            status.error("FAIL_LOAD_FILE_CONFIG", None, ["Falha ao tentar caregar arquivo de configuracao", id])
            return Params(id, None, status)
