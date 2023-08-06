#!/usr/bin/env python
# -*- coding: utf-8 -*-

from devdoo.data_rest import DataRest


class Services(object):
    def __init__(self, message):
        self.MAX_LIMIT = 1000
        self.__data_rest = DataRest(message)

    # ----------------------------------------------------------------
    #
    # Public Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        if hasattr(self, self.__data_rest.action) and self.__data_rest.validate_service(self.version, self.name,
                                                                                       self.id):
            method = getattr(self, self.__data_rest.action)
            method()
        else:
            self.__data_rest.add_error("ACTION ERRADA", self.__data_rest.action + ":: action nao existe no servico")

    # --------------------------------
    # create
    # --------------------------------
    def create(self, collection, scheme):
        self.__data_rest.action = "save"
        self.__data_rest.collection(collection)

        scheme()

        self.__data_rest.owner_id()
        self.__data_rest.owner_last_id()

        self.__data_rest.created_time()
        self.__data_rest.changed_time()

    # --------------------------------
    # find
    # --------------------------------
    def list(self, collection, scheme, max_limit=None):
        self.__max_limit = max_limit
        self.__data_rest.action = "find"
        self.__data_rest.collection(collection)

        scheme()

    # --------------------------------
    # remove
    # --------------------------------
    def remove(self, collection):
        self.__data_rest.action = "remove"
        self.__data_rest.collection(collection)

        #TODO:: Verificar o porque não está sendo passado parametro em services::remove::scheme()
        #TODO:: Verificar services::remove::scheme() é necessário
        self.scheme()

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.__data_rest.ready()

    # --------------------------------
    # scheme
    # --------------------------------
    def scheme(self, scheme):

        self.__query(scheme)

        if self.__data_rest.action == "save":
            # Recupera os dados para salvar na base de dados
            body = self.__data_rest.body
            field_body = {}
            save_data = {}

            # Processa todos os campos de body para colocar em letra minuscula e criar lista de campos validos
            for item in body:
                field = item.replace(' ', '_').lower().strip()
                field_body[field] = body[item]

                # Caso o campo nao esteja registrado no scheme, registra mensagem de error
                if field not in self.__default_fields:
                    self.__data_rest.add_error(125489, "O campo '" + field + "' nao existe.")

            # Processa todos os campos registrados no schema para validar os valores e formatar
            for item in scheme:
                value = '__empty__'
                if (item["field"]) in field_body.keys():
                    value = field_body[(item["field"])]
                    value = self.__check_empty(value)
                value = self.__data_rest.validate_field(item, value)

                if value != None and value != '__empty__' and value != '__error__':
                    if value == '__none__':
                        value = None
                    save_data[(item["field"])] = value

            self.__data_rest.checksum(save_data)
            self.__data_rest.data = save_data

            # Verifica se tem algo para gravar no banco
            if len(save_data.keys()) <= 0:
                self.__data_rest.add_error_required(85545454, "Nao tem nada para gravar no banco de dados")

        elif self.__data_rest.action == "update":
            # TODO:: "UPDATE IMPLEMENTAR COLEÇÃO CHANGE"
            # self.__data_rest.checksum(save_data)
            print "UPDATE IMPLEMENTAR CHANGE"

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        return self.__data_rest.send_database()

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        return self.__data_rest.send_error()

    # --------------------------------
    # update
    # --------------------------------
    def update(self, collection, scheme):
        self.__data_rest.action = "update"
        self.__data_rest.collection(collection)

        scheme()

        self.__data_rest.owner_last_id()
        self.__data_rest.changed_time()

    # ----------------------------------------------------------------
    #
    # Private Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # __fields
    # --------------------------------
    def __fields(self, query):
        fields = {}

        # TODO: Implementar erro para campos não permitidos no serviço
        # print "query.keys()", query.keys()
        # print "default_fields", self.__default_fields

        if 'fields' in query.keys():
            _fields = query["fields"]
            _fields = _fields.strip().split(',')
            for item in _fields:
                fields[item] = True

        if len(fields) == 0 and self.__default_fields != None:
            for item in self.__default_fields:
                fields[item] = True
        fields["_id"] = False
        fields["id"] = True

        return fields

    # --------------------------------
    # __filter
    # --------------------------------
    def __filter(self, query):
        filter = {}
        if 'filter' in query.keys():
            _filter = query["filter"]
            _filter = _filter.strip().split(',')

            for item in _filter:
                item = item.replace(')', "").split('(')
                filter[(item[0])] = item[1]
        return filter

    # --------------------------------
    # __empty__
    # --------------------------------
    def __check_empty(self, value):
        if (len(value) == 0 or value == ''):
            value = '__empty__'

        elif value == 'null':
            value = '__none__'

        return value

    # --------------------------------
    # __limit
    # --------------------------------
    def __limit(self, query):
        limit = self.MAX_LIMIT
        if 'limit' in query.keys():
            limit = query["limit"]
        return limit

    # --------------------------------
    # __query
    # --------------------------------
    def __query(self, scheme):
        query = self.__data_rest.query
        self.__default_fields = ["id"]
        for item in scheme:
            self.__default_fields.append(item['field'])

        # TODO:: Resolver limit
        # self.__max_limit
        # if max_limit == None:
        #    max_limit = self.MAX_LIMIT

        # TODO:: implementar opção para pegar campos de _info
        # fields["_info"] = False

        self.__data_rest.limit = self.__limit(query)
        self.__data_rest.fields = self.__fields(query)
        self.__data_rest.filter = self.__filter(query)
        self.__data_rest.order = {}
        self.__data_rest.cursor = "NDMyNzQyODI3OTQw"
