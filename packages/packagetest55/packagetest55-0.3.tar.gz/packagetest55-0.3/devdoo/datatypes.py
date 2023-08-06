#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, time
from bson.json_util import dumps
from bson.json_util import loads
from bson import Int64
from bson.timestamp import Timestamp
from bson.objectid import ObjectId

import bson, datetime
import unicodedata


class DataTypes():
    def __init__(self):
        pass

    # --------------------------------
    # is_array
    # --------------------------------
    # Verifica se é um array
    # Retorna boolean
    #
    def is_array(self, value):
        return type(value) == list

    # --------------------------------
    # is_boolean
    # --------------------------------
    # Verifica se é boleano
    # Retorna boolean
    #
    def is_boolean(self, value):
        return type(value) == bool

    # --------------------------------
    # is_number
    # --------------------------------
    # Verifica se é número
    # Retorna boolean
    #
    def is_number(self, value):
        return (type(value) == Int64) and value >= -9223372036854775808 and value <= 9223372036854775807

    # --------------------------------
    # is_object
    # --------------------------------
    # Verifica se é objeto
    # Retorna boolean
    # TODO:: Implementar validação recursiva para valores numéricos
    #
    def is_object(self, value):
        return type(value) == dict

    # --------------------------------
    # is_object_id
    # --------------------------------
    # Verifica se é objectId
    # Retorna boolean
    #
    def is_object_id(self, value):
        return type(value) == ObjectId

    # --------------------------------
    # is_timestamp
    # --------------------------------
    # Verifica se é timestamp
    # Retorna boolean
    #
    def is_timestamp(self, value):
        return type(value) == Timestamp

    # --------------------------------
    # is_date
    # --------------------------------
    # Verifica se é uma data
    # Retorna boolean
    #
    def is_date(self, value):
        status = False
        if type(value) == dict and "$date" in value.keys():
            print "value", len(value["$date"]), value["$date"]
            status = len(value["$date"]) == 24,
        return status

    # --------------------------------
    # is_decimal
    # --------------------------------
    # Verifica se é decimal
    # Retorna boolean
    #
    def is_decimal(self, value):
        status = False
        if type(value) == dict and "$numberDecimal" in value.keys():
            status = len(value["$numberDecimal"]) > 0 and len(value["$numberDecimal"]) <= 34
        return status

    # --------------------------------
    # to_array
    # --------------------------------
    # Converte em array todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    def to_array(self, value):
        value = self.to_str(value)
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
    # to_boolean
    # --------------------------------
    # Converte em boolean todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    def to_boolean(self, value):
        value = self.to_str(value)
        if value.lower() in ["true", "1"]:
            value = True
        elif value.lower() in ["false", "0"]:
            value = False
        return value

    # --------------------------------
    # to_decimal
    # --------------------------------
    # Converte em decimal todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    def to_decimal(self, value):
        value = self.to_str(value)
        # Remove todos os caracteres nao numericos
        value = re.sub(r'[^0-9.-]+', '', value)
        if len(value) > 0:
            value = {"$numberDecimal": self.to_str(value)}
        return value

    # --------------------------------
    # to_date
    # --------------------------------
    # Converte em data todas as opções válidas recebidas
    # Retorna o valor original, caso o tipo não seja possível converter
    #
    def to_date(self, value):
        match = re.match(r"([0-9]{4})-([0-1][0-9])-([0-3][0-9])[T ]?([0-2][0-9])?:?([0-5][0-9])?:?([0-5][0-9])?\.?([0-9]{0,9})?Z?\Z", value, re.IGNORECASE)
        if match:
            date_parts = ["0000", "00", "00", "00", "00", "00", "000"]
            index = 0
            for item in match.groups():
                if item:
                    date_parts[index] = item
                    index = index + 1

            if self.__to_date_is_valid(date_parts):
                value = self.__to_date_format(date_parts)
        return value

    # --------------------------------
    # __to_date_is_valid
    # --------------------------------
    # Verifica se uma data é válida
    # Retorna boleano
    # @private
    #
    def __to_date_is_valid(self, parts):
        return (int(parts[1]) <= 12) and (int(parts[2]) <= 31) and (int(parts[3]) <= 23) and (int(parts[4]) <= 59) and (int(parts[5]) <= 59)

    # --------------------------------
    # __to_date_format
    # --------------------------------
    # Converte valor recebido para o formato data
    # Retorna objeto
    # @private
    #
    def __to_date_format(self, parts):
        date_str = str(parts[0] + "-" + parts[1] + "-" + parts[2] + "T" + parts[3] + ":" + parts[4] + ":" + parts[5])
        try:
            date_str = datetime.datetime(*time.strptime(date_str, "%Y-%m-%dT%H:%M:%S")[:6])
            value = {"$date": date_str.strftime("%Y-%m-%dT%H:%M:%S") + "." + str(parts[6][:3]) + "Z"}
        except Exception as inst:
            value = {"error": inst.args[0]}

        return value

    # --------------------------------
    # get_timestamp
    # --------------------------------
    # Retorna a data atual em formato Timestamp
    #
    def get_timestamp(self):
        dt = datetime.datetime.now()
        return dt.strftime("%Y%j%H%M%S") + str(dt.microsecond)

    # --------------------------------
    # to_number
    # --------------------------------
    # Converte o valor recebido para o formato número
    # Retorna inteiro ou o valor original (somente números) se não puder converter
    #
    def to_number(self, value):
        value = self.to_str(value)
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
    def to_object(self, value):
        try:
            value = self.to_str(value)
            value = value.replace("'", '"')
            value = loads(value)
        except:
            pass
        return value

    # --------------------------------
    # to_object_id
    # --------------------------------
    # Converte o valor recebido para o formato ObjectId
    # Retorna ObjectId ou o valor original caso não consiga converter
    #
    def to_object_id(self, value):
        value = self.to_str(value)
        match = re.match("^([0-9a-f]{24})$", value, re.IGNORECASE)
        if match:
            value = match.group(1)
            if len(value) == 24:
                try:
                    value = ObjectId(value)
                except:
                    pass
        return value

    # --------------------------------
    # to_str
    # --------------------------------
    # Converte o valor recebido para o formato String
    # Retorna string
    #
    def to_str(self, value):
        if (type(value) == unicode):
            value = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
            print "TO-STR-UNICODE", value
        else:
            print "TO-STR-STR", value
            value = str(value)
        return value

    # --------------------------------
    # to_timestamp
    # --------------------------------
    # Converte o valor recebido para o formato Timestamp
    # Retorna Timestamp ou o valor original caso não consiga converter
    # TODO:: Implementar outras opções Default de timestamp (s1500, m30, h5, d15, m13, y23)
    #
    def to_timestamp(self, value):
        value = self.to_str(value)

        if value == 'now':
            value = Timestamp(datetime.datetime.utcnow(), 0)
        else:
            try:
                value = re.sub(r'[^0-9]+', '', value)
                value = Timestamp(int(value), 0)
            except:
                pass
        return value
