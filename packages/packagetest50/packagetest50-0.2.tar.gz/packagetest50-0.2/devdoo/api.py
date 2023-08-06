#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from service import Service

class Api(object):
    class Error(Exception):
        pass

    def __init__(self, service_config):

        self.actions = service_config["actions"]
        self.id = service_config["id"]
        self.name = service_config["name"]
        self.schemes = service_config["schemes"]

        self.broker_rest_endpoint = service_config["broker_rest_endpoint"]
        self.broker_db_endpoint = service_config["broker_database_endpoint"]
        context = zmq.Context()

        # adaptador de conexão broker
        self.socket_broker_rest = context.socket(zmq.REP)
        self.socket_broker_rest.connect(self.broker_rest_endpoint)

        # adaptador de conexão worker
        self.socket_broker_database = context.socket(zmq.REQ)
        self.socket_broker_database.connect(self.broker_db_endpoint)

        self.service = None

    def operation(self):
        print 'self.broker_rest_endpoint', self.broker_rest_endpoint
        # Recebe do mensagem do servidor cliente
        message = self.socket_broker_rest.recv()
        self.process(message)
        self.service.action()

        # Verifica se o servico esta pronto
        if self.service.ready():
            print "SELF.BROKER_REST_ENDPOINT", self.broker_rest_endpoint
            print "SELF.BROKER_DB_ENDPOINT", self.broker_db_endpoint

            # Envia mensagem para o servidor de banco de dados
            self.socket_broker_database.send(self.service.send_database())

            # Recebe mensagem do servidor de banco de dados
            # Processa a operacao e envia mensage de retorno para o cliente
            msg = self.socket_broker_database.recv()

            self.socket_broker_rest.send(msg)

        # Em caso de falha
        else:
            # Nao processa a operação e envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.service.send_error())

    def run(self):
        while True:
            try:
                self.operation()
            except Api.Error:
                pass

    def process(self, message):
        self.service = Service(message, self.id, self.name, self.schemes, self.actions, self.custom_service)

    def get_console_service_list(self, server_console, service_id):
        print "SERVICE_ID", service_id
        print "SERVER_CONSOLE", server_console
        return server_console[service_id]