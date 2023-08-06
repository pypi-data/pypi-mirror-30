#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import unicodedata
from bson import Int64
from bson.timestamp import Timestamp
from bson.objectid import ObjectId



# TODO:: Testar possivel falha em str(inst.args)
class Check:
    def __init__(self):
        pass

    # --------------------------------
    # is_array
    # --------------------------------
    # Verifica se é um array
    # Retorna boolean
    #
    @staticmethod
    def is_array(value):
        return type(value) == list

    # --------------------------------
    # is_boolean
    # --------------------------------
    # Verifica se é boleano
    # Retorna boolean
    #
    @staticmethod
    def is_boolean(value):
        return type(value) == bool

    # --------------------------------
    # is_service_config
    # --------------------------------
    # Verifica se o objeto de configuração de serviços é válido
    @staticmethod
    def is_service_config(configs):
        keys = ["id", "type", "service_id", "ip"]
        status = False

        if type(configs) == dict:
            status = True
            for item in keys:
                if item not in configs.keys():
                    status = False
        return status

    # --------------------------------
    # is_date
    # --------------------------------
    # Verifica se é uma data
    # Retorna boolean
    #
    @staticmethod
    def is_date(value):
        status = False
        if (type(value) == dict) and ("$date" in value.keys()):
            status = (len(value["$date"]) == 24)
        return status

    # --------------------------------
    # is_decimal
    # --------------------------------
    # Verifica se é decimal
    # Retorna boolean
    #
    @staticmethod
    def is_decimal(value):
        status = False
        if (type(value) == dict) and ("$numberDecimal" in value.keys()) and re.match("""^-?[0-9]+\.?[0-9]*$""", value["$numberDecimal"]):
            status = (len(value["$numberDecimal"]) > 0) and (len(value["$numberDecimal"]) <= 34)
        return status

    # --------------------------------
    # is_default
    # --------------------------------
    @staticmethod
    def is_default(item_scheme):
        return 'default' in item_scheme.keys()

    # --------------------------------
    # is_empty
    # --------------------------------
    # Verifica se o valor do campo não está vazio ou é do tipo js null
    @staticmethod
    def is_empty(value):
        try:
            if type(value) == unicode:
                value = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
            else:
                value = str(value)
        except Exception:
            value = ''

        # Verifica se o campo é diferente de string e se não está vazio
        return (len(value) == 0) or (value == '')

    # --------------------------------
    # is_number
    # --------------------------------
    # Verifica se é número
    # Retorna boolean
    #
    @staticmethod
    def is_number(value):
        return (type(value) == Int64) and (value >= -9223372036854775808) and (value <= 9223372036854775807)

    # --------------------------------
    # is_object
    # --------------------------------
    # Verifica se é objeto
    # Retorna boolean
    # TODO:: Implementar validação recursiva para valores numéricos
    #
    @staticmethod
    def is_object(value):
        return (type(value) == dict) and ("error" not in value.keys())

    # --------------------------------
    # is_object_id
    # --------------------------------
    # Verifica se é objectId
    # Retorna boolean
    #
    @staticmethod
    def is_object_id(value):
        return type(value) == ObjectId

        # --------------------------------

    # is_scheme
    # --------------------------------
    @staticmethod
    def is_scheme(scheme):
        if type(scheme) == dict:
            list_scheme = ["$currentDate", "$inc", "$min", "$max", "$mul", "$rename", "$set", "$setOnInsert", "$unset"]
            for key in scheme.keys():
                if key in list_scheme:
                    return True
        return False

    # --------------------------------
    # is_string
    # --------------------------------
    # Verifica se é string
    # Retorna boolean
    #
    @staticmethod
    def is_string(value):
        return (type(value) == unicode) or (type(value) == str)

    # --------------------------------
    # is_timestamp
    # --------------------------------
    # Verifica se é timestamp
    # Retorna boolean
    #
    @staticmethod
    def is_timestamp(value):
        return type(value) == Timestamp
