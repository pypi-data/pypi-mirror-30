#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import os
import sys
from check import Check
from config import Config
from convert import Convert
from status import Status


class Core(object):
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):

        self.status = Status()

    # --------------------------------
    # init_config
    # --------------------------------
    # Recupera informações de configurações do broker
    def init_config(self):
        # Tenta pegar configurações docker
        devdoo_config = os.environ.get('devdoo')

        # Caso não tenha sucesso
        if not devdoo_config:
            # Tenta pegar configurações de arquivo local
            devdoo_config = self.__config_local()

        if Check.is_service_config(devdoo_config):
            return Config(devdoo_config, self.status)
        else:
            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])
            return None

    # --------------------------------
    # __config_local
    # --------------------------------
    # Recupera informações de configuração em arquivo local
    def __config_local(self):
        config_local = None
        file_open = None

        if len(sys.argv) > 1:
            # Recupera o endereço do arquivo de configuração
            path_file = str(sys.argv[1])
            # Verifica se o endereço do arquivo é válido
            if (type(path_file) == str) and (".yml" in path_file):
                try:
                    # Abre o arquivo
                    file_yml = open(path_file, "r")
                    # Converte o arquivo em objeto
                    file_open = yaml.load(file_yml)
                except Exception as inst:
                    self.status.error("CONFIGURATION_SERVICE", None,
                                      ["Arquivo de configuracao nao encontrado"])
                    config_local = None

            # Verifica se o arquivo é válido e se existe configurações de serviços nele
            if (file_open is not None) and ("services" in file_open.keys()):
                # Processa o arquivo
                for item in file_open["services"]:
                    services = file_open["services"][item]
                    if "environment" in services:
                        environment = services["environment"]
                        if "devdoo" in environment:
                            devdoo = environment["devdoo"]
                            devdoo = Convert.to_object(devdoo)
                            if Check.is_object(devdoo):
                                # Recupera as configurações devdoo necessárias
                                config_local = devdoo
                            else:
                                self.status.error("CONFIGURATION_SERVICE", None,
                                                  ["Arquivo de configuracao nao e um 'object' valido"])
                        else:
                            self.status.error("CONFIGURATION_SERVICE", None,
                                              ["Arquivo de configuracao encontrou falhas no grupo 'devdoo'"])
                    else:
                        self.status.error("CONFIGURATION_SERVICE", None,
                                          ["Arquivo de configuracao encontrou falhas no grupo 'environment'"])
            else:
                self.status.error("CONFIGURATION_SERVICE", None,
                                  ["Arquivo de configuracao não possui o grupo 'services'"])
        else:
            self.status.error("CONFIGURATION_SERVICE", None,
                              ["Nao foi indicado nenhum endereco de arquivo de configuracao"])
        return config_local
