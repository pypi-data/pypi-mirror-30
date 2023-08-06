#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from bson.json_util import loads
from datatypes import DataTypes

class Broker(object):
    class Error(Exception):
        pass

    def __init__(self, broker_id, console_service_list):
        # Inicia os tipos de dados
        self.__data_types = DataTypes()

        # Cria contexto ZMQ
        context = zmq.Context()

        # Inicializa o poll set
        self.poller = zmq.Poller()

        # Abre porta para o Restify (frontend)
        self.socket_frontend = context.socket(zmq.ROUTER)
        self.socket_frontend.bind("tcp://*:" + self.__data_types.to_str(broker_id))
        self.poller.register(self.socket_frontend, zmq.POLLIN)

        # Abre portas para os Serviços
        self.dic_services = {}
        for service_item in console_service_list:
            # Define o endpoint do serviço
            service_id = self.__data_types.to_str(service_item["service_id"])
            endpoint = "tcp://*:" + service_id

            # Abre portas para os Serviços no backend
            socket_backend = context.socket(zmq.DEALER)
            socket_backend.bind(endpoint)

            # TODO:: Implementar Lista de serviços do mesmo tipo
            # Armazena a conexão do backend no stack
            self.dic_services[service_id] = socket_backend

        # Inicializa variável de conexão
        self.socket_backend = None

    # --------------------------------
    # operation
    # --------------------------------
    # Permuta pacotes entre o frontend e o backend
    #
    def operation(self):
        # Poller de sockets
        socks = dict(self.poller.poll())

        # Verifica se o socket chegou do REST ou Serviço
        if socks.get(self.socket_frontend) == zmq.POLLIN:
            # Recebe mensagem do Restify
            message = self.socket_frontend.recv_multipart()

            # Converte mensagem para json
            package = loads(message[2])
            print "BROKER PACKAGE", package

            # Recupera o socket de conexao do serviço
            self.socket_backend = self.dic_services[self.__data_types.to_str(package["service_id"])]
            print "BROKER: MESSAGE", self.__data_types.to_str(package["service_id"])

            # Verifica se o socket é valido
            if self.socket_backend:
                # Registra o socket no poller ZMQ para dar acesso aos workers
                self.poller.register(self.socket_backend, zmq.POLLIN)

                # Envia ao Service Work a mensagem com pacote de dados
                self.socket_backend.send_multipart(message)
            else:
                # Caso contrario retorna para o cliente sem realizar nenhuma alteração
                self.socket_frontend.send_multipart(message)

        # Verifica se o socket retornou do Service Worker
        if socks.get(self.socket_backend) == zmq.POLLIN:
            # Recebe do Service Worker
            message = self.socket_backend.recv_multipart()
            print "WORKER: MESSAGE", self.__data_types.to_str(message)

            # Retorna ao Restify
            self.socket_frontend.send_multipart(message)
            self.poller.unregister(self.socket_backend)

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #
    def run(self):
        while True:
            try:
                self.operation()
            except Broker.Error:
                pass

    # --------------------------------
    # process
    # --------------------------------
    # Assinatura do método process para sobrescrita
    #
    def process(self, data):
        raise Broker.Error("`process` should be overriden")
