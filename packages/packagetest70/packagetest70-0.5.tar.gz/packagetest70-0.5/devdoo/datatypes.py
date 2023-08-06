#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import datetime
import unicodedata

from bson import Int64
from bson.json_util import loads
from bson.timestamp import Timestamp
from bson.objectid import ObjectId

# TODO:: Testar possivel falha em str(inst.args)
class DataTypes:
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

    # --------------------------------
    # to_array
    # --------------------------------
    # Converte em array todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    @staticmethod
    def to_array(value):
        # Verifica se a string está no formato array
        if re.match(r"\[([\s\S]*)\]\Z", value, re.IGNORECASE):
            try:
                value = value.replace("'", '"')
                value = loads(value)
            except Exception as inst:
                value = {"error": str(inst.args)}
        # Caso contrário tentar converter para array
        elif re.match("""^([^,'";]+,[ ]?)+([^,'";]+)$""", value, re.IGNORECASE):
            value = value.split(",")
        return value

    # --------------------------------
    # to_boolean
    # --------------------------------
    # Converte em boolean todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    @staticmethod
    def to_boolean(value):
        if value.lower() in ["true", "1"]:
            value = True
        elif value.lower() in ["false", "0"]:
            value = False
        return value

    # --------------------------------
    # to_date
    # --------------------------------
    # Converte em data todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    @staticmethod
    def to_date(value):
        regex = r"([0-9]{4})-([0-1][0-9])-([0-3][0-9])[T ]?([0-2][0-9])?:?([0-5][0-9])?:?([0-5][0-9])?\.?([0-9]{0,9})?Z?\Z"
        match = re.match(regex, value, re.IGNORECASE)
        if match:
            date_parts = ["0000", "00", "00", "00", "00", "00", "000"]
            index = 0
            for item in match.groups():
                if item is not None:
                    date_parts[index] = item
                    index = index + 1

            if DataTypes.to_date_is_valid(date_parts):
                value = DataTypes.to_date_format(date_parts)
        return value

    # --------------------------------
    # to_date_is_valid
    # --------------------------------
    # Verifica se uma data é válida
    # Retorna boleano
    # @private
    #
    @staticmethod
    def to_date_is_valid(parts):
        return (int(parts[1]) <= 12) and (int(parts[2]) <= 31) and (int(parts[3]) <= 23) and (int(parts[4]) <= 59) and (int(parts[5]) <= 59)

    # --------------------------------
    # to_date_format
    # --------------------------------
    # Converte valor recebido para o formato data
    # Retorna objeto
    # @private
    #
    @staticmethod
    def to_date_format(parts):
        date_str = str(parts[0] + "-" + parts[1] + "-" + parts[2] + "T" + parts[3] + ":" + parts[4] + ":" + parts[5])
        try:
            date_str = datetime.datetime(*time.strptime(date_str, "%Y-%m-%dT%H:%M:%S")[:6])
            value = {"$date": date_str.strftime("%Y-%m-%dT%H:%M:%S") + "." + str(parts[6][:3]) + "Z"}
        except Exception as inst:
            value = {"error": str(inst.args)}

        return value

    # --------------------------------
    # to_decimal
    # --------------------------------
    # Converte em decimal todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    @staticmethod
    def to_decimal(value):
        # Remove todos os caracteres nao numericos
        value = re.sub(r'[^0-9.-]+', '', value)
        if len(value) > 0:
            value = {"$numberDecimal": DataTypes.to_str(value)}
        return value

    # --------------------------------
    # to_number
    # --------------------------------
    # Converte o valor recebido para o formato número
    # Retorna inteiro ou o valor original (somente números) se não puder converter
    #
    @staticmethod
    def to_number(value):
        # Remove todos os caracteres não numéricos
        value = re.sub(r'[^0-9-]+', '', value)
        if len(value) > 0:
            value = Int64(long(value))
        return value

    # --------------------------------
    # to_object
    # --------------------------------
    # Converte o valor recebido para o formato objeto
    # Retorna objeto ou o valor original caso não consiga converter
    #
    @staticmethod
    def to_object(value):
        try:
            value = value.replace("'", '"')
            value = loads(value)
        except Exception as inst:
            value = {"error": str(inst.args)}
        return value

    # --------------------------------
    # to_object_id
    # --------------------------------
    # Converte o valor recebido para o formato ObjectId
    # Retorna ObjectId ou o valor original caso não consiga converter
    #
    @staticmethod
    def to_object_id(value):
        match = re.match("^([0-9a-f]{24})$", value, re.IGNORECASE)
        if match:
            value = match.group(1)
            if len(value) == 24:
                try:
                    value = ObjectId(value)
                except Exception as inst:
                    value = {"error": str(inst.args)}
        return value

    # --------------------------------
    # to_str
    # --------------------------------
    # Converte o valor recebido para o formato String
    # Retorna string
    #
    @staticmethod
    def to_str(value):
        try:
            if type(value) == unicode:
                value = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
            else:
                value = str(value)
        except Exception as inst:
            value = {"error": str(inst.args)}
        return value

    # --------------------------------
    # to_timestamp
    # --------------------------------
    # Converte o valor recebido para o formato Timestamp
    # Retorna Timestamp ou o valor original caso não consiga converter
    # TODO:: Implementar outras opções Default de timestamp (s1500, m30, h5, d15, m13, y23)
    #
    @staticmethod
    def to_timestamp(value):
        if value == 'now':
            value = Timestamp(datetime.datetime.utcnow(), 0)
        else:
            try:
                value = re.sub(r'[^0-9]+', '', value)
                value = Timestamp(int(value), 0)
            except Exception as inst:
                value = {"error": str(inst.args)}
        return value
