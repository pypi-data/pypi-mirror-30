#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import os
import sys
from check import Check
from status import Status
from console import Console


class DevdooBase(object):
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        self.id = None
        self.status = Status()

    # --------------------------------
    # init_config
    # --------------------------------
    # Recupera informações de configurações do broker
    def init_config(self, instance):

        # Tenta pegar configurações docker
        self.id = os.environ.get('devdoo')

        # Caso não consiga pegar o id do serviço no docker
        if not self.id:
            # Tenta pegar configurações de arquivo local
            self.id = self.__config_local()

        config = None
        if self.id is not None:
            config = Console.load_config(self.id, self.status)

        # Cria objeto de configuração e registra o identificador do serviço na instancia do tipo de config do serviço especifico
        # Neste momento está registando somente o id do serviço, não tem nenhuma informação do serviço no config ainda
        config = instance(config, self.status)

        if config.ready() is False:
            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])

        return config

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
                    self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao nao encontrado"])
                    config_local = None

            # Verifica se o arquivo é válido e se existe configurações de serviços nele
            if (file_open is not None) and ("services" in file_open.keys()):
                # Processa o arquivo
                for item in file_open["services"]:
                    services = file_open["services"][item]
                    if "environment" in services:
                        environment = services["environment"]
                        if "devdoo" in environment:
                            # Recupera as configurações devdoo
                            value = environment["devdoo"]
                            # Verifica se recebeu configuração de devdoo válida
                            if (Check.is_string(value) is True) and (Check.is_empty(value) is False):
                                config_local = value
                            else:
                                self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao nao e um 'devdoo' valido"])
                        else:
                            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao encontrou falhas no grupo 'devdoo'"])
                    else:
                        self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao encontrou falhas no grupo 'environment'"])
            else:
                self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao não possui o grupo 'services'"])
        else:
            self.status.error("CONFIGURATION_SERVICE", None, ["Nao foi indicado nenhum endereco de arquivo de configuracao"])

        return config_local
