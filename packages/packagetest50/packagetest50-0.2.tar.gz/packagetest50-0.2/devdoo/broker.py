#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from bson.json_util import loads
from datatypes import DataTypes

class Broker(object):
    class Error(Exception):
        pass

    def __init__(self, broker_id, console_service_list):
        self.__data_types = DataTypes()
        context = zmq.Context()


        # Initialize poll set
        self.poller = zmq.Poller()

        # Abre porta para o Restify (frontend)
        self.socket_frontend = context.socket(zmq.ROUTER)
        self.socket_frontend.bind("tcp://*:" + self.__data_types.toStr(broker_id))
        self.poller.register(self.socket_frontend, zmq.POLLIN)

        # Abre portas para os services
        self.dicServices = {}
        for service_item in console_service_list:
            service_id = self.__data_types.toStr(service_item["service_id"])
            endpoint = "tcp://*:" + service_id

            # Abre portas para os Services (backend)
            socket_backend = context.socket(zmq.DEALER)

            socket_backend.bind(endpoint)

            # TODO:: Implementar Lista de serviços do mesmo tipo
            self.dicServices[service_id] = socket_backend

        self.socket_backend = None

    def operation(self):
        socks = dict(self.poller.poll())

        if socks.get(self.socket_frontend) == zmq.POLLIN:
            # Recebe mensagem do Restify
            message = self.socket_frontend.recv_multipart()

            # Converte mensagem para json
            package = loads(message[2])
            print "BROKER PACKAGE", package

            # Recupera o socket de conexao do serviço
            self.socket_backend = self.dicServices[self.__data_types.toStr(package["service_id"])]
            print "BROKER: MESSAGE", self.__data_types.toStr(package["service_id"])

            # Verifica se o socket é valiso
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


            print "OPOPOPOPOPOPOPOPOPOPOPO", message
            # Retorna ao Restify
            self.socket_frontend.send_multipart(message)
            self.poller.unregister(self.socket_backend)

    def run(self):
        while True:
            try:
                self.operation()
            except Broker.Error:
                pass

    def process(self, data):
        raise Broker.Error("`process` should be overriden")
