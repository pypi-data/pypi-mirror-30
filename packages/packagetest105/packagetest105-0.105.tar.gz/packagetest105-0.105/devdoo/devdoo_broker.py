#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from zmq.sugar.socket import Socket
from devdoo_base import DevdooBase
from pack import Pack
from config_broker import ConfigBroker
from stack import Stack
from services import Services

from connection import Connection

# TODO:: Enviar para o servidor console a informação de falha de configuração
# TODO:: Envia para o console mensagem de erro de serviço não disponível
class DevdooBroker(DevdooBase):
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
        self.__ready = False


        self.connection = Connection()
        self.connection.load()


        super(DevdooBroker, self).__init__()


        self.config = self.init_config(ConfigBroker)
        self.stack = Stack()

        # Inicializa variáveis default
        self.service_socket = None
        self.socket_frontend = None

        # Verifica se o arquivo de configuração foi inicalizado corretamente
        if self.config.ready():
            # Cria contexto ZMQ
            self.context = zmq.Context()
            # Inicializa o poll set
            self.poller = zmq.Poller()

            self.status.show("SERVICE_ID", [self.config.id])
            self.__init()
        else:
            self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", self.config.id])
            self.status.to_print()


    # --------------------------------
    # __init
    # --------------------------------
    def __init(self):
        if self.status.ready():
            # Cria objeto de conexão para receber interações do rest
            self.socket_frontend = self.context.socket(zmq.ROUTER)

            # Cria um socket de comunicação e configura porta de entrada para receber interações do rest
            self.socket_frontend.bind(self.config.endpoint)

            # Registra na lista de sockets o socket de entrada
            self.poller.register(self.socket_frontend, zmq.POLLIN)

            # Cria lista de serviços (stack)
            self.__services =  Services(self.config.services, self.status)

            self.status.show("SERVICE_INIT", [self.config.type, self.config.id, self.config.endpoint])
            self.run()
        else:
            self.status.error("INVALID_SERVICE", None, ["FALHA NA INICIALIZACAO DO SERVICO", self.config.id])
            self.status.to_print()

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
            self.service_socket = self.__find_service(message)

            #print "AAAAself.service_socket", self.service_socket

            # Verifica se o socket é valido
            if self.service_socket.ready() and type(self.service_socket.backend) == Socket:
                print "SOCKET VALIDO ENVIOU ADIANTE", ">----->>>>"
                # Registra o socket no poller ZMQ para dar acesso aos workers
                self.poller.register(self.service_socket.backend, zmq.POLLIN)

                # Envia ao Service Work a mensagem com pacote de dados
                self.service_socket.backend.send_multipart(message)
                print "SOCKET VALIDO VOLTOU", "<<<<-----<"

            else:
                print "FALHOU, VOLTOU PARA REST", "<<<<-----<"
                # Caso contrario retorna para o cliente sem realizar nenhuma alteração

                #print "self.service_socket.backend", self.service_socket.backend
                self.status.to_print()

                # message[2] = self.service_socket.backend
                self.socket_frontend.send_multipart(message)

        # Verifica se o socket retornou do Service Worker
        if socks.get(self.service_socket.backend) == zmq.POLLIN:
            # Recebe do Service Worker
            message = self.service_socket.backend.recv_multipart()

            # Retorna ao Restify
            self.socket_frontend.send_multipart(message)
            self.poller.unregister(self.service_socket.backend)

    # --------------------------------
    # process
    # --------------------------------
    # Assinatura do método process para sobrescrita
    #
    def process(self, data):
        raise DevdooBroker.Error("`process` should be overriden")

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #

    def run(self):
        while True:
            try:
                self.operation()
            except DevdooBroker.Error:
                pass
                # except Exception as inst:
                # print "BROKER::RUN::ERROR", inst.args

    # --------------------------------
    # __find_service
    # --------------------------------
    def __find_service(self, message):
        service = None

        # Prepara configurações recebidas do rest
        pack = Pack(message, self.status)

        # Verifica se o pacote de configurações é válido
        if pack.ready():
            # Recupera configurações do cliente
            service = self.__services.find(pack.service_id)

            #print "service====>>>>"
            #service.show()


        # Cria e retorna objeto de conexão
        return self.stack.socket(pack, service, self.status)
