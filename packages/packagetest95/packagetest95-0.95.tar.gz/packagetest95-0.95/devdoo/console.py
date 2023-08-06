#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)
BROKER_IP = 'localhost'
if HOST_IP[:3] == '10.':
    BROKER_IP = '10.10.0.1'

print 'HOSTNAME:', HOST_NAME
print 'HOST IP:', HOST_IP
print 'BROKER_IP:', BROKER_IP

BROKER_DATABASE_ENDPOINT_A = 'tcp://localhost:41234'
BROKER_DATABASE_ENDPOINT_B = 'tcp://localhost:41640'
BROKER_DATABASE_ENDPOINT_C = 'tcp://localhost:43210'
MONGO_IP = 'localhost'
if HOST_IP[:3] == '10.':
    BROKER_DATABASE_ENDPOINT_A = 'tcp://10.30.0.1:41234'
    BROKER_DATABASE_ENDPOINT_B = 'tcp://10.30.0.1:41640'
    BROKER_DATABASE_ENDPOINT_C = 'tcp://10.30.0.1:43210'
    MONGO_IP = '10.50.0.1'

print 'HOSTNAME:', HOST_NAME
print 'HOST IP:', HOST_IP
print 'BROKER_DATABASE_ENDPOINT_A:', BROKER_DATABASE_ENDPOINT_A
print 'BROKER_DATABASE_ENDPOINT_B:', BROKER_DATABASE_ENDPOINT_B
print 'BROKER_DATABASE_ENDPOINT_C:', BROKER_DATABASE_ENDPOINT_C
print 'MONGO_IP:', MONGO_IP

import socket

HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)
BROKER_REST_ENDPOINT = 'tcp://localhost:23210'
BROKER_DATABASE_ENDPOINT = 'tcp://localhost:30188'

# Verifica se esta executando no Docker ou On-line
if HOST_IP[:3] == '10.':
    BROKER_REST_ENDPOINT = 'tcp://10.10.0.1:23210'
    BROKER_DATABASE_ENDPOINT = 'tcp://10.30.0.1:30188'

print 'HOSTNAME:', HOST_NAME
print 'HOST IP:', HOST_IP
print 'BROKER_REST_ENDPOINT:', BROKER_REST_ENDPOINT
print 'BROKER_DATABASE_ENDPOINT:', BROKER_DATABASE_ENDPOINT

# load_devdoo_brokers
server_console = {
    "5abe46fd83566949ecc10121": {
        "id": "5abe46fd83566949ecc10121",
        "name": "Broker-RS90",
        "type": "devdoo-brokers",
        "network": {
            "ip": "",
            "port": "10121"
        },
        "version": 1.0,
        "services":
            [
                {
                    "id": "7b85814a9f68d0ad190c4d84",
                    "name": "domains",
                    "ip": BROKER_IP,
                    "service_id": "21234",
                    "connections": 0,
                    "errors": 0
                },
                {
                    "id": "7b85814a9f68d0ad190c4d84",
                    "name": "log",
                    "ip": BROKER_IP,
                    "service_id": "23210",
                    "connections": 0,
                    "errors": 0
                },
                {
                    "id": "7b85814a9f68d0ad190c4d84",
                    "name": "dental",
                    "ip": BROKER_IP,
                    "service_id": "21640",
                    "connections": 0,
                    "errors": 0
                }
            ]},
    "5abe46fd83566949ecc30188": {
        "id": "5abe46fd83566949ecc30188",
        "name": "Broker-DB45",
        "type": "devdoo-brokers",
        "network": {
            "ip": "",
            "port": "30188"
        },
        "version": 1.0,
        "services": [
            {
                "id": "7b85814a9f68d0ad190c4d86",
                "name": "domains",
                "service_id": "41234",
                "connections": 0,
                "errors": 0
            },
            {
                "id": "7b85814a9f68d0ad190c4d86",
                "name": "log",
                "service_id": "43210",
                "connections": 0,
                "errors": 0
            },
            {
                "id": "7b85814a9f68d0ad190c4d86",
                "name": "dental",
                "service_id": "41640",
                "connections": 0,
                "errors": 0
            }
        ]
    },
    "41234":
        {
            "id": "9885814a9f68d0ad190c4d79",
            "name": "domains",
            "broker_database_endpoint": BROKER_DATABASE_ENDPOINT_A,
            "mongodb_ip": MONGO_IP,
            "mongodb_port": 27017,
            "service_id": "41234",
            "connections": 0,
            "errors": 0
        },
    "41640":
        {
            "id": "a885814a9f68d0ad190c4d7a",
            "name": "dental",
            "broker_database_endpoint": BROKER_DATABASE_ENDPOINT_B,
            "mongodb_ip": MONGO_IP,
            "mongodb_port": 27017,
            "service_id": "41640",
            "connections": 0,
            "errors": 0
        },
    "5abe46fd83566949ecc43210":
        {
            "id": "a885814a9f68d0ad190c4d7a",
            "name": "log",
            "broker_database_endpoint": BROKER_DATABASE_ENDPOINT_C,
            "mongodb_ip": MONGO_IP,
            "mongodb_port": 27017,
            "service_id": "43210",
            "connections": 0,
            "errors": 0
        },

    "5abe46fd83566949ecc23210":
        {
            "id": "5abe46fd83566949ecc23210",
            "name": "log",
            "type": "devdoo-service",
            "network": {
                "ip": "",  # ip da instância
                "port": "23210"  # porta do serviço log no primeiro broker (rest)
            },
            "version": 1.0,  # versão
            "database": {
                "id": "6355814a9f68d0ad190c4d53",
                "network": {
                    "ip": "",  # ip da instância
                    "port": "43210"  # porta do serviço log no primeiro broker (rest)
                },
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
                            "scheme": {},
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
                                "public": []
                            },
                            "scheme": {
                                "$set": [
                                    "type_array",
                                    "type_boolean",
                                    "type_number"
                                ]
                            },
                            "action": "insert",
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
                            "scheme": {},
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
                            "scheme": {},
                            "collection": "messages",
                            "action": "remove",
                            "type": "list",
                            "max_limit": 100
                        }
                    }
                }
            },
            "endpoints": {
                "broker_rest": BROKER_REST_ENDPOINT,
                "broker_database": BROKER_DATABASE_ENDPOINT
            }
        }
}


# TODO:: Mudar estutura de configuração de scheme e actions
class Console:
    def load_config(self, id):
        return server_console[id]

    def ready(self):
        return True
