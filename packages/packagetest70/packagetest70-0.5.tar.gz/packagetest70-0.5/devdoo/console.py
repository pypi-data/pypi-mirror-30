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

server_console = {
    "5abe46fd83566949ecc10121": [
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
    ],
    "5abe46fd83566949ecc30188": [
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
    ],

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
    "43210":
        {
            "id": "a885814a9f68d0ad190c4d7a",
            "name": "log",
            "broker_database_endpoint": BROKER_DATABASE_ENDPOINT_C,
            "mongodb_ip": MONGO_IP,
            "mongodb_port": 27017,
            "service_id": "43210",
            "connections": 0,
            "errors": 0
        }
}


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


server_console_scheme = {
    "23210":
        {
            "uid": "4885814a9f68d0ad190c4d76",
            "id": "23210",
            "name": "log",
            "broker_rest_endpoint": BROKER_REST_ENDPOINT,
            "broker_database_endpoint": BROKER_DATABASE_ENDPOINT,
            "service_id": "23210",
            "errors": 0,

            "schemes": {
                "type_array": {"type": "array", "info": "Array", "version": "1.0"},
                "type_boolean": {"type": "boolean", "info": "Boolean", "version": "1.0"},
                "type_number": {"type": "number", "info": "Number", "version": "1.0", "min_value": "100", "max_value": "3000", "required": "true"},
                "type_decimal": {"type": "decimal", "info": "Number Decimal", "version": "1.0"},
                "type_object": {"type": "object", "info": "Object", "version": "1.0"},
                "type_timestamp": {"type": "timestamp", "info": "Timestamp", "version": "1.0"},
                "type_objectid": {"type": "object_id", "info": "ObjectId", "version": "1.0"},
                "type_enum": {"type": "enum", "info": "Enum", "version": "1.0", "enum": ["M", "F", "34"]},
                "type_string": {"type": "string", "info": "String", "version": "1.0"},
                "type_date": {"type": "date", "info": "Date", "version": "1.0"},
                "type_bola": {"type": "bola", "info": "Bola", "version": "1.0"},

                "code": {"type": "number", "info": "Código do erro", "version": "1.0"},
                "script": {"type": "object", "info": "Nome do script", "version": "1.0"},
                "container": {"type": "object", "info": "ID do container", "version": "1.0"},
                "instance": {"type": "object", "info": "ID da instância", "version": "1.0"},
                "created_at": {"type": "date", "info": "Horário da ocorrência", "version": "1.0"},
                "user": {"type": "object", "info": "Código do usuário", "version": "1.0"},
                "service": {"type": "object", "info": "Código do serviço", "version": "1.0"},
                "type": {"type": "string", "info": "Tipo do (error|warn|info|log)", "version": "1.0"},
                "message": {"type": "string", "info": "Detalhes extras", "version": "1.0"}
            },

            "actions": {
                "get": {
                    # --------------------------------
                    # messages
                    # --------------------------------
                    "/1.0/devdoo/log/system/messages": {
                        "action": {
                            "scheme": [
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
                            "database_action": "find",
                            "collection": "messages",
                            "result_type": "list"
                        }
                    }
                },
                "put": {},
                "post": {
                    # --------------------------------
                    # mensagens
                    # --------------------------------
                    "/1.0/devdoo/log/system/add-message": {
                        "action": {
                            "scheme": [
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
                            "database_action": "insert",  # TODO: Mudar o nome da operação de database para operation
                            "collection": "messages",
                            "result_type": "item"
                        }
                    }
                },
                "delete": {
                    # --------------------------------
                    # mensagens
                    # --------------------------------
                    "/1.0/devdoo/log/system/remove-message": {
                        "action": {
                            "scheme": [],
                            "collection": "operators",
                            "database_action": "remove",
                            "result_type": "list",
                        }
                    }
                }
            }
        }
}


class Console:

    def services_config(self, id):
        return server_console[id]