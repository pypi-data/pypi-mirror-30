#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from check import Check
from convert import Convert
from status import Status
from bson.json_util import dumps


# TODO: Refatorar classe completa Package
class Package:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, message):
        self.__ready = False

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
        self.body = {}  # Todos os dados que precisam ser transportados entre os serviços
        self.id = None  # Id da conexão, gerado no REST
        self.lenght_in = 0  # Tamanho do pacote de entrada
        self.lenght_out = 0  # Tamanho do pacote de saída
        self.service = None  # Identificador do serviço
        self.service_id = None  # Id do serviço a ser executado
        self.database_id = None  # Id numérico do banco de dados
        self.open = True  # Indica se a conexão está aberta/fechada 0=close|1=open
        self.source = None  # Uri da api
        self.success = False  # Status boleano indicando sucesso ou falha na operação
        self.time = {
            "time_start": 0,  # Momento de inicio da conexão no REST
            "service": 0,  # Momento de inicio da operação no serviço
            "database": 0  # Momento de inicio da operação do serviço de banco
        }

        self.message = message
        self.status = Status()

    # --------------------------------
    # active_service
    # --------------------------------
    def active_service(self, database_id):
        self.database_id = database_id
        self.active_port = database_id

    # --------------------------------
    # decode
    # --------------------------------
    def decode(self, status):
        self.status = status
        self.__ready = False

        if Check.is_string(self.message):
            package = Convert.to_object(self.message)

            print "PACKAGE---->>>", package

            if Check.is_object(package):
                self.__ready = True
                self.active_port = package["active_port"]
                self.action = package["action"]
                self.alerts = {
                    "error": package["alerts"]["error"],
                    "log": package["alerts"]["log"],
                    "warn": package["alerts"]["warn"],
                    "info": package["alerts"]["info"]
                }
                self.app_id = package["app_id"]
                self.api_key = package["api_key"]
                self.body = package["body"]
                self.id = package["id"]
                self.lenght_in = sys.getsizeof(self.message)
                self.lenght_out = package["lenght_out"]
                self.service = Convert.to_str(package["service"])
                self.service_id = Convert.to_str(package["service_id"])
                self.database_id = Convert.to_str(package["database_id"])
                self.open = package["open"]
                self.source = package["source"]
                self.success = package["success"]
                self.time = {
                    "time_start": package["time"]["time_start"],
                    "service": package["time"]["service"],
                    "database": package["time"]["database"]
                }
                self.database = "db" + self.database_id + self.service
                self.token = "xvz1evFS4wEEPTGEFPHBog:L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg"
            else:
                self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])
        else:
            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])

    # --------------------------------
    # is_valid
    # --------------------------------
    def is_valid(self):
        self.__check_package()
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
        return dumps(self.package)

    # --------------------------------
    # __check_package
    # --------------------------------
    def __check_package(self):
        # Verifica se mensagem é string
        if (type(self.message) == list) and len(self.message) >= 3:
            # Converte a mensagem recebida do servidor rest para objeto
            self.package = Convert.to_object(self.message[2])

            # Verifica se o pacote de mensagem é do tipo objeto válido
            if Check.is_object(self.package):
                # Verifica se o pacote de mensagem é válido
                self.__ready = self.__check_params(self.package)

                if self.__ready is True:
                    self.active_port = Convert.to_str(self.package["active_port"])
                else:
                    self.status.error("INVALID_PACKAGE", None, ["Pacote de comunicacao invalido"])
                    self.package["alerts"] = {"error": self.status.to_list(), "log": None, "warn": None, "info": None}
                    self.package["success"] = False
                    self.package["status"] = 0

    # --------------------------------
    # __check_params
    # --------------------------------
    # Verifica se o pacote de comunicação é válido
    def __check_params(self, package):
        errors = []

        # Verifica se no pacote existe o identificador do serviço
        if "action" not in package.keys():
            errors.append("ACTION")

        if "active_port" not in package.keys():
            errors.append("ACTIVE PORT")

        if "alerts" not in package.keys():
            errors.append("ALERTS")

        if "body" not in package.keys():
            errors.append("BODY")

        if "lenght_in" not in package.keys():
            errors.append("LENGHT_IN")

        if "lenght_out" not in package.keys():
            errors.append("LENGHT_OUT")

        if "open" not in package.keys():
            errors.append("OPEN")

        if "source" not in package.keys():
            errors.append("SOURCE")

        if "success" not in package.keys():
            errors.append("SUCCESS")

        if "time" not in package.keys():
            errors.append("TIME")

        if "api_key" not in package.keys():
            errors.append("API_KEY")

        if "id" not in package.keys():
            errors.append("ID")

        if "service" not in package.keys():
            errors.append("SERVICE")

        if "service_id" not in package.keys():
            errors.append("SERVICE ID")

        if len(errors) > 0:
            self.status.error("INVALID_PACKAGE_PARAMS", None, ["Pacote de comunicacao nao tem:", (",".join(errors))])
            return False
        return True
