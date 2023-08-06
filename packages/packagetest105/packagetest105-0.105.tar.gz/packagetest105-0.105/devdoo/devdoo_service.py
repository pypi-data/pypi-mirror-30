#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from devdoo_base import DevdooBase
from convert import Convert
from service import Service
from config_service import ConfigService


# TODO:: Enviar para o servidor console a informação de falha de configuração
class DevdooService(DevdooBase):
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
        super(DevdooService, self).__init__()

        self.config = self.init_config(ConfigService)

        # Inicializa variáveis default
        self.service = None

        # Verifica se o arquivo de configuração foi inicalizado corretamente
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

        if self.__is_start_service() is True:
            # Cria contexto ZMQ
            context = zmq.Context()

            # Adaptador de conexão broker
            self.socket_broker_rest = context.socket(zmq.REP)
            self.socket_broker_rest.connect(self.config.endpoint["broker_rest"])

            # Adaptador de conexão worker
            self.socket_broker_database = context.socket(zmq.REQ)
            self.socket_broker_database.connect(self.config.endpoint["broker_database"])

            self.status.show("SERVICE_INIT", [self.config.type])
            self.run()
        else:
            self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", self.config.id])
            self.status.to_print()

    # --------------------------------
    # __is_start_service
    # --------------------------------
    def __is_start_service(self):

        # Vai até o servidor console buscar informações de configurações do serviços assoaciadas eo identificador do serviço
        # Recupera o identificador do serviço 'devdoo-broker' no arquivo yml
        self.config.console_load_pre_config("devdoo-service")

        # Retorna status indicando se houve algum erro no processo de configuração do serviço
        return self.status.ready()

    # --------------------------------
    # operation
    # --------------------------------
    # Executa a ação do Serviço
    #
    # TODO:: Implementar melhorias na verificação de disponibilidade do serviço para serguir adiante, chegando todos os tipos que serão enviados
    def operation(self):
        # Recebe do mensagem do servidor cliente
        message = self.socket_broker_rest.recv()

        # Inicia o Serviço
        self.process(message)

        # Executa a ação do Serviço
        self.service.action()

        # Verifica se o servico está pronto
        if self.service.ready():
            print "SOCKET VALIDO ENVIOU ADIANTE", "----->>>>"
            # Envia mensagem para o servidor de base de dados
            self.socket_broker_database.send(self.service.send_database())

            # Recebe mensagem do servidor de base de dados
            # Envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.socket_broker_database.recv())
            print "SOCKET VALIDO VOLTOU", "----->>>>"

        # Em caso de falha
        else:
            # Nao processa a operação e envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.service.send_error())

    # --------------------------------
    # process
    # --------------------------------
    # Inicia o Serviço
    #
    # TODO:: Mudar a forma como deverá ser configurado o serviço
    def process(self, message):
        self.service = Service(message, self.config)

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
            except DevdooService.Error:
                pass

                # except Exception as inst:
                #    print "API::RUN::ERROR", inst.args
