#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from core import Core
from convert import Convert
from service_db import ServiceDB

# TODO:: Implementar autoconfiguração do serviço, comunicação com console admin
class DevdooDatabases(Core):
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
        super(DevdooDatabases, self).__init__()



        # Serviço a ser executado
        self.service = None
        self.config = self.init_config()

        if self.config.ready():
            self.__start()
        else:
            # TODO:: Enviar para o servidor console a informação de falha de configuração
            print Convert.to_str("AAA - FALHA NA INICIALIZACAO DO DEVDOO-BROKER-SERVICE")
            print "ERROR", self.status.to_list()

    # --------------------------------
    # __start
    # --------------------------------
    def __start(self):
        if self.__is_start_services() is True:
            # Cria contexto ZMQ
            context = zmq.Context()

            # Adaptador de conexão
            self.socket_frontend = context.socket(zmq.REP)
            self.socket_frontend.connect(self.config.broker_database_endpoint)

            print "AAAA- RUN"

            self.run()

        else:
            print "BBB - FALHA NA INICIALIZAÇÃO DO DEVDOO-BROKER-SERVICE"

    # --------------------------------
    # __is_start_services
    # --------------------------------
    def __is_start_services(self):
        self.config.load_devdoo_databases()
        return self.config.ready()

    # --------------------------------
    # console_service_list
    # --------------------------------
    # Obtém da console a lista de configuração
    #
    # TODO:: Remover console_service_list, implementar sistema de autoconfiguração
    def console_service_list(self, server_console, service_id):
        return server_console[service_id]

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
    # TODO:: Mudar a forma como deverá ser configurado o serviço
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
            except DevdooDatabases.Error:
                pass
                # except Exception as inst:
                #    print "API_DB::RUN::ERROR", inst.args
