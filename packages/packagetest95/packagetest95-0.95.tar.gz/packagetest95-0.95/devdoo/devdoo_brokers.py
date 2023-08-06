#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from zmq.sugar.socket import Socket
from core import Core
from convert import Convert
from package import Package


class DevdooBrokers(Core):
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
        super(DevdooBrokers, self).__init__()

        self.config = self.init_config()

        # Inicializa variável de conexão
        self.socket_backend = None

        if self.config.ready():
            # Cria contexto ZMQ
            self.context = zmq.Context()
            # Inicializa o poll set
            self.poller = zmq.Poller()

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
            broker_endpoint = "tcp://*:" + Convert.to_str(self.config.service_id)

            # Abre porta para o Restify (frontend)
            self.socket_frontend = self.context.socket(zmq.ROUTER)
            self.socket_frontend.bind(broker_endpoint)
            self.poller.register(self.socket_frontend, zmq.POLLIN)

            self.run()
        else:
            print "BBB - FALHA NA INICIALIZAÇÃO DO DEVDOO-BROKER-SERVICE"

    # --------------------------------
    # __is_start_services
    # --------------------------------
    def __is_start_services(self):
        status = False

        list_services = self.config.load_devdoo_brokers()

        if self.config.ready():
            # Abre portas para os Serviços
            self.available_services = {}
            for item in list_services:
                # Define o endpoint do serviço
                service_id = Convert.to_str(item["service_id"])
                endpoint = "tcp://*:" + service_id

                # Abre portas para os Serviços no backend
                socket_backend = self.context.socket(zmq.DEALER)
                socket_backend.bind(endpoint)

                # TODO:: Implementar Lista de serviços do mesmo tipo
                # TODO:: Aprimorar registro do serviço no stack
                # Armazena a conexão do backend no stack
                self.available_services[service_id] = socket_backend

            if len(self.available_services.keys()) > 0:
                status = True

        return status

    # --------------------------------
    # operation
    # --------------------------------
    # Permuta pacotes entre o frontend e o backend
    #
    # TODO:: Verificar se existe um serviço para o service_id solicitado antes de tentar pegar na lista
    # TODO:: Verificar se o serviço está disponível antes de tentar fazer conexão
    # TODO:: Verificar se a mensagem foi corretamente convertida de string para dic antes de tentar pegar um elemento
    # TODO:: Procurar formas de desregistrar sockets que não obtiveram respostas dentro do tempo limite
    def operation(self):
        # Poller de sockets
        socks = dict(self.poller.poll())

        # Verifica se o socket chegou do REST ou Serviço
        if socks.get(self.socket_frontend) == zmq.POLLIN:
            # Recebe mensagem do Restify
            message = self.socket_frontend.recv_multipart()

            # Recupera o socket de conexao do serviço
            self.socket_backend = self.__find_socket(message)

            # Verifica se o socket é valido
            if type(self.socket_backend) == Socket:
                print "SOCKET VALIDO ENVIOU ADIANTE", "----->>>>"
                # Registra o socket no poller ZMQ para dar acesso aos workers
                self.poller.register(self.socket_backend, zmq.POLLIN)

                # Envia ao Service Work a mensagem com pacote de dados
                self.socket_backend.send_multipart(message)
                print "SOCKET VALIDO VOLTOU", "----->>>>"

            else:
                print "FALHOU, VOLTOU PARA REST", "----->>>>"
                # Caso contrario retorna para o cliente sem realizar nenhuma alteração
                message[2] = self.socket_backend
                self.socket_frontend.send_multipart(message)

        # Verifica se o socket retornou do Service Worker
        if socks.get(self.socket_backend) == zmq.POLLIN:
            # Recebe do Service Worker
            message = self.socket_backend.recv_multipart()

            # Retorna ao Restify
            self.socket_frontend.send_multipart(message)
            self.poller.unregister(self.socket_backend)

    # --------------------------------
    # process
    # --------------------------------
    # Assinatura do método process para sobrescrita
    #
    def process(self, data):
        raise DevdooBrokers.Error("`process` should be overriden")

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #

    def run(self):
        while True:
            try:
                self.operation()
            except DevdooBrokers.Error:
                pass
            #except Exception as inst:
            #    print "BROKER::RUN::ERROR", inst.args

    # --------------------------------
    # __find_socket
    # --------------------------------
    def __find_socket(self, message):
        package = Package(message)

        # Verifica se mensagem é string
        if package.is_valid() is True:
            if package.active_port in self.available_services.keys():
                return self.available_services[package.active_port]
            else:
                # TODO:: Envia para o console mensagem de erro de serviço não disponível
                self.status.error("INVALID_SERVICE", None, ["Servico nao disponível no servidor BROKER", package.active_port])


        return package.to_string()
