#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from bson.json_util import dumps
from bson.json_util import loads
from bson import Int64
import bson, datetime
import unicodedata


class DataTypes():
    def __init__(self):
        pass

    # --------------------------------
    # isArray
    # --------------------------------
    def isArray(self, value):
        return type(value) == list

    # --------------------------------
    # isBoolean
    # --------------------------------
    def isBoolean(self, value):
        return type(value) == bool

    # --------------------------------
    # isNumber
    # --------------------------------
    def isNumber(self, value):
        return (type(value) == Int64) and value >= -9223372036854775808 and value <= 9223372036854775807

    # --------------------------------
    # isObject
    # --------------------------------
    # TODO:: Implementar validação recursiva para valores numéricos
    def isObject(self, value):
        return type(value) == dict

    # --------------------------------
    # isDecimal
    # --------------------------------
    def isDecimal(self, value):
        status = False
        if type(value) == dict and "$numberDecimal" in value.keys():
            status = len(value["$numberDecimal"]) <= 34
        return status

    # --------------------------------
    # toArray
    # --------------------------------
    # Converte em array todas as opções válidas recebidas
    # Retorna o valor original case o tipo não seja possível converter
    def toArray(self, value):
        value = self.toStr(value)
        # Verifica se a string está no formato array
        if re.match(r"\[([\s\S]*)\]\Z", value, re.IGNORECASE):
            try:
                value = value.replace("'", '"')
                return loads(value)
            except:
                pass
        # Caso contrário tentar converter para array
        elif re.match("""^([^,'";]+,[ ]?)+([^,'";]+)$""", value, re.IGNORECASE):
            value = value.split(",")
        return value

    # --------------------------------
    # toBoolean
    # --------------------------------
    # Converte em boolean todas as opções válidas recebidas
    # Retorna o valor original case o tipo não seja possível converter
    def toBoolean(self, value):
        value = self.toStr(value)
        if value.lower() in ["true", "1"]:
            value = True
        elif value.lower() in ["false", "0"]:
            value = False
        return value


    # --------------------------------
    # toDecimal
    # --------------------------------
    def toDecimal(self, value):
        value = self.toStr(value)
        # Remove todos os caracteres nao numericos
        value = re.sub(r'[^0-9.-]+', '', value)
        if len(value) > 0:
            value =  {"$numberDecimal": self.toStr(value)}
        return value

    # --------------------------------
    # toNumber
    # --------------------------------
    def toNumber(self, value):
        value = self.toStr(value)
        # Remove todos os caracteres nao numericos
        value = re.sub(r'[^0-9-]+', '', value)
        if len(value) > 0:
            value = Int64(long(value))
        return value
    # --------------------------------
    # toObject
    # --------------------------------
    def toObject(self, value):
        try:
            value = self.toStr(value)
            value = value.replace("'", '"')
            value = loads(value)
        except:
            pass
        return value

    # --------------------------------
    # toStr
    # --------------------------------
    def toStr(self, value):
        if (type(value) == unicode):
            value = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
            print "TO-STR-UNICODE", value
        else:
            print "TO-STR-STR", value
            value = str(value)
        return value
