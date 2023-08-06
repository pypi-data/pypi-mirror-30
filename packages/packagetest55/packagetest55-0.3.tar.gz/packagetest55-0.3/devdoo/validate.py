#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pydash
from error import Error
from devdoo.datatypes import DataTypes


# TODO:: Verificar tipos inexistentes
class Validate(object):
    def __init__(self, custom_service=None):
        self.__error = Error()
        self.__custom_service = custom_service
        self.__data_types = DataTypes()

    # ----------------------------------------------------------------
    #
    # Public Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # add_error
    # --------------------------------
    # Adiciona erro na lista de erros
    #
    def add_error(self, code, message):
        self.__error.add(code, message)

    # --------------------------------
    # add_error
    # --------------------------------
    # Adiciona erro do tipo requerido na lista de erros retornada
    #
    def add_error_required(self, code, message):
        self.__error.add_required(code, message)

    # --------------------------------
    # add_errors
    # --------------------------------
    # Adiciona uma lista de erros na lista de erros retornada
    #
    def add_errors(self, list_errors):
        if list_errors is not None:
            for error in list_errors:
                self.__error.add(error['code'], error['message'])

    # --------------------------------
    # error_to_list
    # --------------------------------
    # Converte os erros para lista
    # Retorna lista
    #
    def error_to_list(self):
        return self.__error.to_list()

    # --------------------------------
    # ready
    # --------------------------------
    # Indica se está pronto
    # Retorna boleano
    #
    def ready(self):
        return self.__error.ready

    # --------------------------------
    # has_error
    # --------------------------------
    # Indica se há erros
    # Retorna boleano
    #
    def has_error(self):
        return self.__error.has_error

    # ----------------------------------------------------------------
    #
    # types
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # array
    # --------------------------------
    # Valida campo do tipo array
    # Retorna array
    #
    def array(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte para array
        value = self.__data_types.to_array(value)

        # Verifica se o resultado do tipo convertido é um array válido
        if not self.__data_types.is_array(value):
            # Registra mensagem de erro no serviço de log e retona ao cliente
            field_name = field["field"]
            self.__error.addx("TYPE_INVALID_ARRAY", [field_name, original_value])
            value = self.__check_value(value)
        return value

    # --------------------------------
    # boolean
    # --------------------------------
    # Valida campo do tipo boleano
    #
    # Retorna boleano
    #
    def boolean(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte para boleano
        value = self.__data_types.to_boolean(value)

        # Verifica se o resultado do tipo convertido é um boleano válido
        if not self.__data_types.is_boolean(value):
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.add_error(4505845, "O valor do campo '" + field[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor entre true | false | 0 | 1")
            value = self.__check_value(value)

        return value

    # --------------------------------
    # date
    # --------------------------------
    # Valida campo do tipo data
    #
    # Exemplo: 9999-12-31T23:59:59.999
    # AAAA-MM-DDTHH:MM:SS.mmm
    # AAAA-MM-DD
    # Retorna Timestamp
    def date(self, field, value):
        original_value = value = self.__data_types.to_str(value)

        # Converte para boleano
        value = self.__data_types.to_date(value)

        # Verifica se o resultado do tipo convertido é uma data válida
        if not self.__data_types.is_date(value):
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.add_error(4505845, "O valor do campo '" + field[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize os formatos de data AAAA-MM-DD ou AAAA-MM-DDTHH:MM:SS.mmm")
            if (type(value) == dict) and ("error" in value.keys()):
                self.add_error(74585545, "Data inválida:: " + original_value + " ::" + value["error"])

            value = self.__check_value(original_value)

        return value

    # --------------------------------
    # decimal (float)
    # --------------------------------
    # Valida campo do tipo número decimal
    # Retorna float decimal
    #
    def decimal(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte valor para número
        value = self.__data_types.to_decimal(value)

        # Verifica se o resultado do tipo convertido é um decimal válido
        if self.__data_types.is_decimal(value):
            pass
            # TODO:: Implementar min/max para decimal
            # min_value / max_value
            # error_min = self.__min_value_decimal(field, value)
            # error_max = self.__max_value_decimal(field, value)
            # if error_min or error_max:
            #    value = '__error__'
        else:
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.add_error(8545255,
                           "O campo '" + field[
                               "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor entre -x até x.")
            value = self.__check_value(value)

        return value

    # --------------------------------
    # enum
    # --------------------------------
    # Valida campo do tipo opções de enumeração
    # Aceita somente opções string
    #
    # type: enum
    # enum:["M", "F", "34"]
    # is_required = self.__required(item_scheme)
    #
    def enum(self, item_scheme, value):
        original_value = self.__data_types.to_str(value)

        options = self.__type(item_scheme, "enum")

        # Converte para string
        value = self.__data_types.to_str(value)

        if value == '__empty__' or value == '__none__':
            self.add_error(4505845, "O valor do campo '" + item_scheme[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor entre: " + self.__data_types.to_str(options))
            value = '__error__'

        if value not in options:
            self.add_error(4505845, "O valor do campo '" + item_scheme[
                "field"] + "' :: '" + value + "', deve conter na lista de opcoes: " + self.__data_types.to_str(options))
            value = '__error__'

        return value

    # --------------------------------
    # number
    # --------------------------------
    # Valida campo do tipo número longo
    #
    # type: number
    # min_value: 150
    # max_value: 300
    # formater:??
    #
    def number(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte valor para número
        value = self.__data_types.to_number(value)

        # Verifica se o resultado do tipo convertido é um número válido
        if self.__data_types.is_number(value):
            # min_value / max_value
            error_min = self.__min_value(field, value)
            error_max = self.__max_value(field, value)
            if error_min or error_max:
                value = '__error__'
        else:
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.add_error(8545255,
                           "O campo '" + field["field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor entre -x até x.")
            value = self.__check_value(value)

        return value

    # --------------------------------
    # object
    # --------------------------------
    # Valida campo do tipo object
    #
    # type: object
    #
    def object(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte valor para número
        value = self.__data_types.to_object(value)

        # Verifica se o resultado do tipo convertido é objeto válido
        if not self.__data_types.is_object(value):
            self.add_error(4505845, "O valor do campo '" + field[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor do tipo object")
            value = self.__check_value(value)

        return value

    # --------------------------------
    # object_id
    # --------------------------------
    # Valida campo do tipo objectId
    #
    # type: object_id
    # Exemplo: 5abb87da835669241478b102
    def object_id(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte valor para número
        value = self.__data_types.to_object_id(value)

        # Verifica se o resultado do tipo convertido é um object_id válido
        if not self.__data_types.is_object_id(value):
            self.add_error(4505845, "O valor do campo '" + field[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor do tipo object_id")
            value = self.__check_value(value)

        return value

    # --------------------------------
    # string
    # --------------------------------
    #
    # Valida campo do tipo string
    #
    # type: string
    # modifier: ["uppercase", "..."]
    # min_length: 5
    # max_length: 15
    # formater:??
    #
    def string(self, field, value):
        value = self.__data_types.to_str(value)
        # Remove elementos indesejados da string
        value = pydash.strings.escape(value).strip()
        value = self.__clean_value(value)

        # min_length / max_length
        error_min = self.__min_length(field, value)
        error_max = self.__max_length(field, value)
        if error_min or error_max:
            value = '__error__'
            return value

        # Implementa modificadores
        return self.__modifier(field, value)

    # --------------------------------
    # timestamp
    # --------------------------------
    # Valida campo do tipo timestamp
    # Exemplo: 1522239066
    def timestamp(self, field, value):
        original_value = self.__data_types.to_str(value)

        # Converte valor para número
        value = self.__data_types.to_timestamp(value)

        # Verifica se o resultado do tipo convertido é um timestamp válido
        if not self.__data_types.is_timestamp(value):
            self.add_error(4505845, "O valor do campo '" + field[
                "field"] + "' nao pode ser '" + original_value + "', vazio ou null, utilize um valor do tipo timestamp")
            value = self.__check_value(value)

        return value

    # ----------------------------------------------------------------
    #
    # Init Process
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # field
    # --------------------------------
    def __field(self, item_scheme_name, item_scheme, value, action=None):
        # Implementa valor default em caso do campo não receber valor do cliente
        field_name = item_scheme_name

        field_value = self.__default(item_scheme, value)
        field_type = item_scheme["type"]

        if hasattr(self, field_type):
            # Recupera o método do type que deverá ser executado
            method = getattr(self, field_type)
            field_value = method(item_scheme, field_value)
        else:
            field_value = '__error__'
            self.add_error(854857, "O tipo do campo '" + item_scheme["field"] + " -> " + field_type + "' nao existe.")
            return field_name, field_value

        # Verifica se o campo e requerido
        if field_value == '__empty__' or field_value == '':
            self.__required(item_scheme)
        # if action is not None:
        #    field_name, field_value = self.__custom(action, item_scheme, field_value, self.__error)

        return field_name, field_value

    def field_save(self, item_scheme_name, item_scheme, value, action=None):

        print "item_scheme_name", item_scheme_name, "value", value,

        field_name, field_value = self.__field(item_scheme_name, item_scheme, value, action=None)
        # Verifica se o nome do campo é dot
        if "." in field_name:
            field_name, field_value = self.__field_dot(field_name, field_value)

        return field_name, field_value

    def field_update(self, item_scheme_name, item_scheme, value, action=None):
        return self.__field(item_scheme_name, item_scheme, value, action=None)

    # ----------------------------------------------------------------
    #
    # Private Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # __custom
    # --------------------------------
    def __custom(self, action, item_scheme, field_value, error):
        field_name = item_scheme["field"]

        if action in item_scheme.keys():
            # Verifica se a acao existe na instancia do servico
            if hasattr(self.__custom_service, item_scheme["field"] + "_" + action):
                method = getattr(self.__custom_service, item_scheme["field"] + "_" + action)
                field_name, field_value = method(field_name, field_value, error)

        return field_name, field_value

    # --------------------------------
    # __default
    # --------------------------------
    def __default(self, field, value):
        if value == '__empty__' or value == None:
            if "default" in field.keys():
                value = field["default"]
        return value

    # --------------------------------
    # __clean_value
    # --------------------------------
    def __clean_value(self, value):
        if value == '__empty__' or value == '__none__':
            value = ''
        return value

    # --------------------------------
    # __check_empty
    # --------------------------------
    def __check_empty(self, value):
        if (len(value) == 0 or value == ''):
            value = '__empty__'

        elif value == 'null':
            value = '__none__'

        return value

    # --------------------------------
    # __check_value
    # --------------------------------
    def __check_value(self, value):
        if value == '__empty__' or value == '__none__':
            value = ''
        else:
            value = '__error__'

        return value

    # --------------------------------
    # __lodash
    # --------------------------------
    def __lodash(self, action, value):
        if action == 'camel_case':
            value = pydash.strings.camel_case(value)
        elif action == 'clean':
            value = pydash.strings.clean(value)
        elif action == 'decapitalize':
            value = pydash.strings.decapitalize(value)
        elif action == 'escape':
            value = pydash.strings.escape(value)
        elif action == 'lowercase':
            value = pydash.strings.to_lower(value)
        elif action == 'kebab_case':
            value = pydash.strings.kebab_case(value)
        elif action == 'uppercase':
            value = pydash.strings.to_upper(value)
        elif action == 'upper_first':
            value = pydash.strings.upper_first(value)
        elif action == 'startcase':
            value = pydash.strings.start_case(value)
        elif action == 'titlecase':
            value = pydash.strings.title_case(value)
        elif action == 'unescape':
            value = pydash.strings.unescape(value)

        return value

    # --------------------------------
    # __max_length
    # --------------------------------
    def __max_length(self, field, value):
        has_error = False
        max_length = self.__type(field, "max_length")
        if (max_length is not None) and (len(value) > max_length):
            message = "O tamanho máximo permitido é (" + self.__data_types.to_str(max_length) + "), foi recebido (" + self.__data_types.to_str(
                len(value)) + ")."
            self.__register_error(field, value, "MAX LENGTH", message)
            has_error = True
        return has_error

    # --------------------------------
    # __min_length
    # --------------------------------
    def __min_length(self, field, value):
        has_error = False
        min_length = self.__type(field, "min_length")
        if (min_length is not None) and (len(value) < min_length):
            message = "O tamanho mínimo permitido é (" + self.__data_types.to_str(min_length) + "), foi recebido (" + self.__data_types.to_str(
                len(value)) + ")."
            self.__register_error(field, value, "MIN LENGTH", message)
            has_error = True
        return has_error

    # --------------------------------
    # __max_value
    # --------------------------------
    def __max_value(self, field, value):
        has_error = False
        max_value = self.__type(field, "max_value")
        if (max_value is not None) and self.__data_types.is_number(value):
            message = "O valor máximo permitido é (" + self.__data_types.to_str(max_value) + "), foi recebido (" + self.__data_types.to_str(
                value) + ")."
            self.__register_error(field, value, "MAX VALUE", message)
            has_error = True
        return has_error

    # --------------------------------
    # __min_value
    # --------------------------------
    def __min_value(self, field, value):
        has_error = False
        min_value = self.__type(field, "min_value")
        if (min_value is not None) and self.__data_types.is_number(value):
            message = "O valor mínimo permitido é (" + self.__data_types.to_str(min_value) + "), foi recebido (" + self.__data_types.to_str(
                value) + ")."
            self.__register_error(field, value, "MIN VALUE", message)
            has_error = True
        return has_error

    # --------------------------------
    # __modifier
    # --------------------------------
    def __modifier(self, field, value):
        modifier = self.__type(field, "modifier")
        if modifier is not None:
            for action in modifier:
                value = self.__lodash(action, value)
        return value

    # --------------------------------
    # __options
    # --------------------------------
    def __options(self):
        pass

    # --------------------------------
    # __register_error
    # --------------------------------
    def __register_error(self, scheme, value, code, message=None):
        self.__error.add_field(scheme["field"], value, code, message)
        return '__error__'

    # --------------------------------
    # __required
    # --------------------------------
    def __required(self, item_scheme):
        is_required = self.__type(item_scheme, "required")
        if is_required:
            self.__error.add_field_required(item_scheme['field'], "REQUIRED", "Campo requerido")
        return is_required

    # --------------------------------
    # __type
    # --------------------------------
    def __type(self, scheme, field):
        result = None
        if field in scheme.keys():
            result = scheme[field]
        return result

    # --------------------------------
    # __validate
    # --------------------------------
    def __validate(self, value):
        pass

    def __field_dot(self, field_name, field_value):
        d = {}

        field_name_first, field_name = field_name.split(".", 1)

        # Pegar a primeira chave do nome campo
        # Pagar as partes restantes e converter em objeto com valor

        # Converte string em objetos
        def put(d, dot_string, value):
            if "." in dot_string:
                key, rest = dot_string.split(".", 1)
                if key not in d:
                    d[key] = {}
                put(d[key], rest, value)
            else:
                d[dot_string] = value

        put(d, field_name, field_value)
        return field_name_first, d
