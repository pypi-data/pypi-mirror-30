#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import hashlib
from bson.json_util import dumps
from bson.json_util import loads
from devdoo.validate import Validate
from datatypes import DataTypes

#TODO: Verificar necessidade de uso da data_rest, transferir para a datarest e remover
class DataRest():
    def __init__(self, message):
        self.__data_types = DataTypes()
        self.__validate = Validate()
        self.decode(message)

    # --------------------------------
    # add_error
    # --------------------------------
    def add_error(self, code, message):
        self.__validate.add_error(code, message)


    # --------------------------------
    # add_error_required
    # --------------------------------
    def add_error_required(self, code, message):
        print "ERERERERE____", message
        self.__validate.add_error_required(code, message)

    # --------------------------------
    # changed_time
    # --------------------------------
    def changed_time(self):
        self.info["changed_time"] = self.__data_types.toStr(datetime.datetime.utcnow())

    # --------------------------------
    # checksum
    # --------------------------------
    def checksum(self, data):
        md5 = hashlib.md5()
        md5.update(dumps(data))
        self.info["checksum"] = md5.hexdigest()

    # --------------------------------
    # collection
    # --------------------------------
    def collection(self, collection):
        if collection != self.__service:
            list_names = collection.split("_")
            if list_names[0] != self.__service:
                list_names.insert(0, self.__service)
                collection = '_'.join(list_names)

        self.info["database"]["collection"] = collection;
        self.collection_name = collection
        self.__source()

    # --------------------------------
    # created_time
    # --------------------------------
    def created_time(self):
        self.info["created_time"] = self.__data_types.toStr(datetime.datetime.utcnow())

    # --------------------------------
    # owner_id
    # --------------------------------
    def owner_id(self):
        self.info["owner"] = {
            "id": self.token
        }

    # --------------------------------
    # owner_last_id
    # --------------------------------
    def owner_last_id(self):
        self.info["owner"] = {
            "last_id": self.token
        }

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.__validate.ready()

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        message_send = {
            "action": self.action,
            "collection_name": self.collection_name,
            "cursor": self.cursor,
            "data": self.data,
            "database_name": self.database_name,
            "error": self.__validate.error_to_list(),
            "fields": self.fields,
            "filter": self.filter,
            "id": self.id,
            "limit": self.limit,
            "order": {},
            "service_id": self.database_id
        }
        print 'MESSAGE SEND :::::::::::::::::::>>>>>>>>>>>', message_send
        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps(message_send)

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        message_send = {
            "id": self.id,
            "success": False,
            "error": self.__validate.error_to_list()
        }
        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps(message_send)

    # --------------------------------
    # validateService
    # --------------------------------
    def validateService(self, version, service, service_id):
        self.__version = version
        self.__service = service
        self.__service_id = service_id
        if self.__version != self.version or self.__service != self.service or self.__service_id != self.service_id:
            self.__validate.add_error("FALHA DE SERVICE", "Identificador do serviço nao valido")
            return False
        return True

    # --------------------------------
    # validateField
    # --------------------------------
    def validateField(self, field, value):
        return self.__validate.field(field, value)

    # ----------------------------------------------------------------
    #
    # Private Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # decode_service
    # --------------------------------
    def decode(self, message):
        # Prepara o pacote a ser enviado
        _json = loads(message)

        self.action = _json["action"]
        self.body = _json["body"]
        self.id = _json["id"]
        self.info = _json["info"]
        self.query = _json["query"]
        self.service = _json["service"]
        self.service_id = _json["service_id"]
        self.database_id = self.__data_types.toStr(int(_json["service_id"]) + 20000)
        self.token = _json["token"]
        self.version = _json["version"]

        self.group = self.info["application"]["group"]
        self.database_name = "db" + self.database_id + self.service
        self.info["database"] = {"name": self.database_name, "collection": None}

        print 'DECODE', _json

    # --------------------------------
    # __source
    # --------------------------------
    def __source(self):
        self.info["service"]["source"] = "/" + self.__version + "/" + self.group + "/" \
                                         + self.collection_name.replace("_", "/")
