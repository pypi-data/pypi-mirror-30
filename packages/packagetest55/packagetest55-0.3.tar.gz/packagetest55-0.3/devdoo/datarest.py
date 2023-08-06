#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import hashlib, re
from bson.json_util import dumps
from bson.json_util import loads
from devdoo.validate import Validate
from devdoo.filter import Filter
from datatypes import DataTypes

class DataRest():
    def __init__(self, message, custom_service):
        self.__data_types = DataTypes()

        # TODO:: Implementar configuração de limites definido no console para o serviço
        self.__max_limit = 200
        self.__default_limit = 100

        self.__validate = Validate(custom_service)
        self.__filter = None
        self.__data = {}
        self.decode(message)

    def action(self, action):
        self.__action = action

    def cursor(self, cursor):
        self.__cursor = cursor

    def data(self, data):
        self.__data = data
        # Registra o checksum do documento
        self.checksum(data)

    # --------------------------------
    # fields
    # --------------------------------
    def fields(self, fields):
        # Verifica se recebeu uma lista de campos do usuário
        # Verifica se campos são válidos
        # Registra lista de campos solicitados
        if len(self.__fields) > 0:
            list_fields = []
            for item in self.__fields:
                if item in fields:
                    list_fields.append(item)
            self.__fields = list_fields
        else:
            #Registra lista de campos default
            self.__fields = fields


    def method(self):
        return self.__method

    # --------------------------------
    # __limit
    # --------------------------------
    # Define o limite de documentos retornados
    #
    # ?limit=20
    #
    def limit(self, max_limit=0):
        # Condigura o limite default do serviço
        limit = error_limit = self.__default_limit

        # Verifica se o limit da ação foi definido
        if self.__limit > 0:
            # Recupera o limite da operação para validar
            limit = error_limit = self.__limit

            # Verifica se o limite da operação maior do que o maximo permitido pelo serviço
            if limit > self.__max_limit:

                # Caso seja, então registra o limite maximo permitido
                limit = error_max_limit = self.__max_limit

                # Verifica se um limite máximo foi definido pelo desenvolvedor do serviço
                if max_limit > 0 and limit > max_limit:
                    # Caso seja, então registra o limite maximo permitido
                    error_max_limit = max_limit
                    limit = max_limit

                self.add_error(85545454, "O limite máximo (" + self.__data_types.to_str(error_max_limit) + ") foi excedido. Limite solicitado (" + self.__data_types.to_str(error_limit) + ").")

        self.__limit = limit

    def info(self):
        return {
            "owner": {
                "id": self.__token,
                "last_id": self.__token
            }
        }

    # --------------------------------
    # add_error
    # --------------------------------
    def add_error(self, code, message):
        self.__validate.add_error(code, message)

    # --------------------------------
    # add_error_required
    # --------------------------------
    def add_error_required(self, code, message):
        self.__validate.add_error_required(code, message)

    # --------------------------------
    # changed_time
    # --------------------------------
    def changed_time(self):
        self.__changed_time = self.__data_types.to_str(datetime.datetime.utcnow())

    # --------------------------------
    # checksum
    # --------------------------------
    def checksum(self, data):
        md5 = hashlib.md5()
        md5.update(dumps(data))
        self.__checksum = md5.hexdigest()

    # --------------------------------
    # collection
    # --------------------------------
    def collection(self, collection):
        if collection != self.__service:
            list_names = collection.split("_")
            if list_names[0] != self.__service:
                list_names.insert(0, self.__service)
                collection = '_'.join(list_names)
        self.__collection = collection

    # --------------------------------
    # created_time
    # --------------------------------
    def created_time(self):
        self.__created_time = self.__data_types.to_str(datetime.datetime.utcnow())

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.__validate.ready()

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        message = {
            "action": self.__action,
            "collection": self.__collection,
            "connection_id": self.__connection_id,
            "cursor": self.__cursor,
            "data": self.__data,
            "database": self.__database,
            "errors": self.__validate.error_to_list(),
            "fields": self.__fields,
            "filter": self.__filter.to_list(),
            "limit": self.__limit,
            "offset": self.__offset,
            "method": self.__method,
            "result_type": self.__result_type,
            "sort": self.__sort,
            "service_id": self.__database_id,
            "info": self.info()
        }

        print "SEND SAVE", message

        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps(message)

    # --------------------------------
    # send_error
    # --------------------------------
    # Montar mensagem de erro para ser retornada ao servidor rest
    def send_error(self):
        print "----------------------------AQUI"
        return dumps({
            "connection_id": self.__connection_id,
            "message": {
                "success": False,
                "message": "Falha de interação com microserviço",
                "elapsed_time": {"response": "17.000", "server": "7.000"},
                "errors": self.__validate.error_to_list(),
                "query": {
                    "limit": self.__limit,
                    "offset": self.__offset,
                    "fields": self.__fields,
                    "filter": self.__filter.to_list()  # TODO: Preparar filtro para ser retornado ao cliente
                },
            }
        })

    # --------------------------------
    # validate_service
    # --------------------------------
    def validate_service(self, service, service_id):
        print "SERVICE", service
        print "SERVICE_ID", service_id
        # TODO:: Implementar verificação de possivel conflito de unicode em situações não claramente definidas

        if self.__service != service or self.__data_types.to_str(self.__service_id) != self.__data_types.to_str(service_id):
            self.__validate.add_error("FALHA DE SERVICE", "Identificador do serviço nao valido:: " + self.__service + "!=" + service + "::" + self.__data_types.to_str(
                self.__service_id) + "!=" + self.__data_types.to_str(service_id))
            return False
        return True

    # --------------------------------
    # validate_field_save
    # --------------------------------
    def validate_field_save(self, item_scheme_name, item_scheme, value, action=None):
        return self.__validate.field_save(item_scheme_name, item_scheme, value, action)

    # --------------------------------
    # validate_field_update
    # --------------------------------
    def validate_field_update(self, item_scheme_name, item_scheme, value, action=None):
        return self.__validate.field_update(item_scheme_name, item_scheme, value, action)

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
        json = loads(message)

        print "DECODE", json

        self.body = json["body"]

        self.__action = json["action"]
        self.__connection_id = json["connection_id"]
        self.__cursor = json["cursor"]
        self.__fields = json["fields"]
        self.__filter = Filter(json["filter"], self.__validate)  # TODO:: Mudar sistema de error, tirar de dentro do validate
        self.__limit = int(json["limit"])
        self.__info = json["info"]
        self.__method = json["method"]
        self.__offset = int(json["offset"])
        self.__regex = json["regex"]
        self.__search = json["search"]
        self.__service = json["service"]
        self.__service_id = int(json["service_id"])
        self.__sort = json["sort"]
        self.__source = self.__set_source(json["source"])
        self.__token = json["token"]
        self.__version = json["version"]

        # TODO:: Mudar regra de criação de nomes de banco de dados
        self.__database_id = self.__service_id + 20000
        # self.group = self.info["application"]["group"]
        self.__database = "db" + self.__data_types.to_str(self.__database_id) + self.__service
        # self.info["database"] = {"name": self.database_name, "collection": None}

    # --------------------------------
    # __set_source
    # --------------------------------
    # Recupera o id do documento
    def __set_source(self, source):
        # Verificar se o source possui uma id
        # Pegar a id do source
        result = re.search(r"([\s\S]+)([0-9a-f]{24})$", source)
        if result:
            source = result.group(1) + ":id"
            self.__filter.add("_id.eq", result.group(2))

        return source

    # Todo Finalizar sistema de seach e regex
    def __filter_extras(self):
        # self.__prepare_regex()
        self.__prepare_search()
        print "REGEX--------------------->>>", self.__regex
        print "SEARCH--------------------->>>", self.__search
        print "FIELDS--------------------->>>", self.__fields

    def __prepare_regex(self):
        print self.__regex

    # { name: { $regex: "s3", $options: "si" } }
    # or{quantity.lt(20)|price(10)}
    # tags.in( '{ $regex: "s3", $options: "si" }', '{ $regex: "s3", $options: "si" }')
    def __prepare_search(self):
        values, fields = self.__search.split(';')
        values = values.split()
        fields = fields.split(',')
        if len(fields) > 0:
            for item in fields:
                print "---->", item
                for word in values:
                    # self.__filter.add("_id.eq", result.group(2))
                    # print "-............>", item+".in", word
                    print "------->", word
        print "FILTERS", self.__filter.to_list()

    # --------------------------------
    # __set_source
    # --------------------------------

    def source(self):
        return self.__source

    def result_type(self, type):
        self.__result_type = type
