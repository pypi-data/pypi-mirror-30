#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.json_util import dumps
from bson.json_util import loads
from devdoo.validate import Validate

class DataRest_DB():
    def __init__(self, message):
        self.__validate = Validate()
        self.decode(message)

    def action(self):
        return self.__action

    def collection(self):
        return self.__collection

    def data(self):
        return self.__data

    def database(self):
        return self.__database

    def fields(self):
        return self.__fields

    def filter(self):
        return self.__filter

    def limit(self):
        return self.__limit

    def offset(self):
        return self.__offset

    def sort(self):
        return self.__sort


    def result_type(self):
        return self.__result_type

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
    # ready
    # --------------------------------
    def ready(self):
        return self.__validate.ready()

    # --------------------------------
    # send_error
    # --------------------------------
    # TODO:: Melhorar mensagem de retorno em caso de falha
    def send_error(self):
        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps({
            "connection_id": self.__connection_id,
            "errors": self.__validate.error_to_list()
        })

    # --------------------------------
    # send_service
    # --------------------------------
    def send(self):
        print "SEND RESULT----->>>>>>>", {
            "connection_id": self.__connection_id,
            "XXXXXXXXXXX":">>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "message": self.__message_send
        }, "<<<<<-------------"

        # Registrar no stack de log
        # Registrar no stack de analytic
        # Registrar no stack de error
        # Registrar no stack de history
        # self.analyric.add({})

        return dumps({
            "connection_id": self.__connection_id,
            "message": self.__message_send
        })


    # ----------------------------------------------------------------
    #
    # Private Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # decode_service_db
    # --------------------------------
    def decode(self, message):
        # Prepara o pacote a ser enviado
        json = loads(message)

        self.__action = json["action"]
        self.__collection = json["collection"]
        self.__connection_id = json["connection_id"]
        self.__cursor = json["cursor"]
        self.__data = json["data"]
        self.__database = json["database"]
        self.__fields = json["fields"]
        self.__result_type = json["result_type"]
        self.__sort = json["sort"]
        self.__service_id = json["service_id"]
        self.__info = json["info"]
        self.__filter = json["filter"]
        self.__limit = json["limit"]
        self.__offset = json["offset"]
        self.__method = json["method"]
        self.__validate.add_errors(json["errors"])

        print "RECEBE SERVICE", json

        print "FILTER--------------------->>>>>", self.__filter,


    # --------------------------------
    # result
    # --------------------------------
    def result(self, message):
        message["elapsed_time"] = {"response": "17.000", "server": "7.000"}
        message["method"] = self.__method

        if self.__validate.has_error():
            message["errors"] = self.__validate.error_to_list()

        self.__message_send = message
