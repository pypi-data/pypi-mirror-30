#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from service_db import Service_DB

class Api_DB(object):
    class Error(Exception):
        pass

    def __init__(self, service_config):

        broker_database_endpoint = service_config["broker_database_endpoint"]
        self.mongodb_ip = service_config["mongodb_ip"]
        self.mongodb_port = service_config["mongodb_port"]

        context = zmq.Context()

        # adaptador de conexão
        self.socket_frontend = context.socket(zmq.REP)
        self.socket_frontend.connect(broker_database_endpoint)

        self.service = None

    def operation(self):
        # Recebe do mensagem do servidor cliente
        message = self.socket_frontend.recv()
        self.process(message)

        # Processa a operacao e envia mensage de retorno para o cliente
        self.socket_frontend.send(self.service.send())

    def run(self):
        while True:
            try:
                self.operation()
            except Api_DB.Error:
                pass

    def process(self, message):
        self.service = Service_DB(message, self.mongodb_ip, self.mongodb_port)


    def get_console_service_list(self, server_console, service_id):
        return server_console[service_id]