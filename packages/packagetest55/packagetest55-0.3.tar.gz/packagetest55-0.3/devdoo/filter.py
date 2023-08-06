#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
import bson
from bson.regex import Regex
from bson.json_util import dumps
from datatypes import DataTypes


class Filter():
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, params, validate):
        self.__data_types = DataTypes()
        self.__validate = validate
        self.__params = {}
        self.labels = {"item": {}, "list": {}}
        list_params = self.__to_list(params)
        self.__prepare(self.__params, list_params, "item")
        self.__conflict()

    # --------------------------------
    # __str__
    # --------------------------------
    def __str__(self):
        return self.__data_types.to_str(self.__params)

    # --------------------------------
    # to_list
    # --------------------------------
    def to_list(self):
        return self.__params

    # --------------------------------
    # __conflict
    # --------------------------------
    def __conflict(self):
        fields_errors = []

        # Processa a lista de campos default
        for item_check in self.labels["item"]:
            # Retira um item da lista para comparar com outros itens da mesma lista
            for item_field in self.labels["item"]:
                # Caso um campo esteja em conflito com outros campos é adicionado na lista de erros
                if item_check + '.' in item_field:
                    fields_errors.append([item_check, item_field])
        if len(fields_errors) > 0:
            self.__validate.add_error(3363569, "ERROR:: CAMPOS EM CONFLITOS" + self.__data_types.to_str(fields_errors))
            # print "ERROR:: CAMPOS EM CONFLITOS", fields_errors

    # --------------------------------
    # __is_empty
    # --------------------------------
    # Verifica se o valor do campo não está vazio ou é do tipo js null
    def __is_empty(self, item):
        # Verifica se o campo é diferente de string e se não está vazio
        if (len(item) == 0 or item == ''):
            return False

    # --------------------------------
    # add
    # --------------------------------
    #TODO:: implementar self.__data_types = DataTypes()
    def add(self, field, value):
        if type(value) == str:
            filter = self.__data_types.to_str(field + "(" + value + ")")
        else:
            filter = unicode(field + "(" + value + ")")

        self.__prepare(self.__params, [filter], 'item')

    # --------------------------------
    # __prepare
    # --------------------------------
    def __prepare(self, group_params, list_params, type):
        for param in list_params:
            print "PARAM------------------------>>>>", param
            if re.match(r"(?:([\s\S]*|\.(eq|gt|gte|lt|lte|ne|exists|not|in|nin|type))\(([\s\S]+)\))\Z", param, re.IGNORECASE):
                param_match = re.match(r"(?:([\s\S]*|\.(eq|gt|gte|lt|lte|ne|exists|not|in|nin|type))\(([\s\S]+)\))\Z", param, re.IGNORECASE)

                if re.match(r"^([a-z0-9_]+\.?)+$", param_match.group(1), re.IGNORECASE):
                    print "MATCH - Filtro ", param_match.group(1)
                    self.labels[type][param_match.group(1)] = True
                    self.__dot_to_dict(group_params, param_match.group(1), self.__values(param_match.group(3)))
                else:
                    self.__validate.add_error(87541545, "ERROR - Filtro inválido" + self.__data_types.to_str(param_match.group(1)))
                    # print "ERROR - Filtro inválido ", param_match.group(1)

            elif re.match(r"(?:(and|nor)\[([\s\S]*)\])\Z", param, re.IGNORECASE):
                param_match = re.match(r"(?:(and|nor)\[([\s\S]*)\])\Z", param, re.IGNORECASE)

                if not re.match(r"(?:[a-z0-9]+\([\s\S]+\)[^\+])\Z", param_match.group(2), re.IGNORECASE):
                    if re.match(r"^([a-z0-9_]+\.?)+$", param_match.group(1), re.IGNORECASE):
                        group = group_params["$" + param_match.group(1)] = []
                        self.__values_list(group, param_match.group(2), "+")
                    else:
                        self.__validate.add_error(523152, "ERROR FILTRO- de separador '|' nao encontrado" + self.__data_types.to_str(param_match.group(1)))
                        # print "ERROR - Filtro inválido " , param_match.group(1)
                else:
                    self.__validate.add_error(523152, "ERROR FILTRO- de separador '|' nao encontrado" + self.__data_types.to_str(param_match.group(1)))
                    # print "ERROR DE PIPEXXXX------------------>>>>>", param_match.group(2)

            elif re.match(r"(or)\{([\s\S]*)\}\Z", param, re.IGNORECASE):
                param_match = re.match(r"(or)\{([\s\S]*)\}\Z", param, re.IGNORECASE)
                if not re.match(r"(?:[a-z0-9]+\([\s\S]+\)[^|])\Z", param_match.group(2), re.IGNORECASE):
                    if re.match(r"^([a-z0-9_]+\.?)+$", param_match.group(1), re.IGNORECASE):
                        group = group_params["$" + param_match.group(1)] = []
                        self.__values_list(group, param_match.group(2), "|")
                    else:
                        self.__validate.add_error(5454545454, "Filtro inválido" + self.__data_types.to_str(param_match.group(1)))
                        # print "ERROR - Filtro inválido ",  param_match.group(1)
                else:
                    self.__validate.add_error(523152, "ERROR FILTRO- de separador '|' nao encontrado" + self.__data_types.to_str(param_match.group(1)))
                    # print "ERROR DE PIPE------------------>>>>>", param_match.group(2)

            else:
                self.__validate.add_error(5454545454, "Filtro inválido" + self.__data_types.to_str(param_match.group(1)))
                # print "ERROR - Filtro Inválido:: ", param

    # --------------------------------
    # __dot_to_dict
    # --------------------------------
    def __dot_to_dict(self, d, dot_string, value):
        if dot_string == "id": dot_string = "_id"
        options = ["eq", "gt", "gte", "lt", "lte", "ne", "exists", "not", "type", "and", "or", "nor", "in", "nin"]
        if "." in dot_string:
            key, rest = dot_string.split(".", 1)
            if key == "id": key = "_id"
            if key not in d:
                key = key if key not in options else '$' + key
                d[key] = {}
            self.__dot_to_dict(d[key], rest, value)
        elif dot_string in options:
            if type(d) == dict:
                key = '$' + dot_string
                d[key] = self.__check_options_values(dot_string, value)
        else:
            d[dot_string] = value

    # --------------------------------
    # __check_options_values
    # --------------------------------
    def __check_options_values(self, key, value):
        options = ["in", "nin", "and", "or", "nor"]
        if key in options:
            if type(value) != list:
                value = [value]

        count = 0
        for item in value:
            # { name: { $regex: "s3", $options: "si" } }
            # Verifica se é do tipo regex
            if type(item) == str or type(item) == unicode and re.match(r"\/([\s\S]+)\/([\s\S]+)\Z", item, re.IGNORECASE):
                regex = re.match(r"\/([\s\S]+)\/([\s\S]+)\Z", item, re.IGNORECASE)
                value[count] = {
                    "$regex": regex.group(1),
                    "$options": regex.group(2)
                }
                count = count + 1

        return value

    # --------------------------------
    # __to_list
    # --------------------------------
    def __to_list(self, params, sep=";"):
        list_params = []
        if type(params) == str or type(params) == unicode:
            params = params.split(sep)
            for item in params:
                if self.__is_empty(item) != False:
                    list_params.append(item)
        return list_params

    # --------------------------------
    # __values_list
    # --------------------------------
    def __values_list(self, group_params, values, sep):
        list_params = self.__to_list(values, sep)
        if len(list_params) > 0:
            for item in list_params:
                item_filter = {}
                if re.match(r"(?:([\s\S]*|\.(eq|gt|gte|lt|lte|ne|exists|not|in|nin|type))\(([\s\S]+)\))\Z", item, re.IGNORECASE):
                    self.__prepare(item_filter, [item], "list")
                elif re.match(r"(or)\{([\s\S]*)\}\Z", item, re.IGNORECASE):
                    list_items = item.split(sep)
                    self.__prepare(item_filter, list_items, "list")

                if item_filter.keys() > 0:
                    group_params.append(item_filter)

    # --------------------------------
    # __values
    # --------------------------------
    def __values(self, value):

        # Verifica se o valor é do tipo número
        if value.isdigit() or value.replace('.', '', 1).isdigit():
            value = ast.literal_eval(value)

        # Verifica se o valor é do tipo array
        elif "," in value:
            value = value.split(",")
            i = 0
            for item in value:
                if item.isdigit() or item.replace('.', '', 1).isdigit():
                    value[i] = ast.literal_eval(item)
                    i += 1
        # Verifica se é do tipo bolean
        elif value.lower() in ["true", "1"]:
            value = True
        elif value.lower() in ["false", "0"]:
            value = False

        # Verifica se é do tipo objectID
        elif re.match("^[0-9a-f]{24}$", value):
            try:
                value = bson.objectid.ObjectId(self.__data_types.to_str(value))
            except:
                pass

        # Verifica se é do tipo date
        # Verifica se é do tipo timestamp
        # Verifica se é uma lista

        if type(value) == list:
            count = 0;
            # Processa s lista para verificar se os elementos são do tipo ObjectId
            for item in value:
                # Verifica se é do tipo objectId
                if re.match("^[0-9a-f]{24}$", item):
                    try:
                        # Converte string em ObjectId
                        value[count] = bson.objectid.ObjectId(self.__data_types.to_str(item))
                        count = count + 1
                    except:
                        pass

        return value
