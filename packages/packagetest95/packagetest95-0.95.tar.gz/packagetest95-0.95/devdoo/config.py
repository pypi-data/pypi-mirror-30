#!/usr/bin/env python
# -*- coding: utf-8 -*-


from console import Console
from database import DataBase
from pymongo import MongoClient
from pprint import pprint


class Config:
    def __init__(self, config, status):
        self.status = status
        self.__ready = True
        self.id = config["id"]

        print "INIT SERVICE ID::", self.id
        self.console = Console()

    def load_devdoo_services(self):
        self.__ready = False
        config = self.console.load_config(self.id)

        if len(config.keys()) > 1:
            # Define parâmetros globais
            self.name = config["name"]
            self.type = config["type"]
            self.network = config["network"]
            self.version = config["version"]
            self.database = DataBase(config["database"], self.status)
            self.endpoint_broker_rest = config["endpoints"]["broker_rest"]
            self.endpoint_broker_database = config["endpoints"]["broker_database"]
            self.active_service = self.database.active_service()

            # self.schemes = config["schemes"]
            # self.service_id = self.network["port"]
            # self.database_id = self.database["network"]["port"]

            self.__ready = True

    def load_devdoo_databases(self):
        self.__ready = False
        config = self.console.load_config(self.id)
        if len(config.keys()) > 1:
            # Define endpoints de conexão
            self.broker_database_endpoint = config["broker_database_endpoint"]

            mongodb_ip = config["mongodb_ip"]
            mongodb_port = int(config["mongodb_port"])

            self.mongo_server = MongoClient(mongodb_ip, mongodb_port)

            self.__ready = True

    def load_devdoo_brokers(self):
        self.__ready = False
        config = self.console.load_config(self.id)

        if (self.console.ready()):
            self.name = config["name"]
            self.type = config["type"]
            self.network = config["network"]
            self.version = config["version"]
            self.services = config["services"]
            self.service_id = self.network["port"]  # isso vai morrer

            self.__ready = True
            return self.services

    def ready(self):
        if self.status.ready() is False:
            pprint(self.status.to_list())
        return self.status.ready()
