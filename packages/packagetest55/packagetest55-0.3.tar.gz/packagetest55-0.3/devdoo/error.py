#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.json_util import dumps
import requests

class Error():
    def __init__(self):
        self.has_error = False
        self.ready = True
        self.__list_errors = []

        self.error_messages = {
            "TYPE_INVALID_ARRAY": {
                "code": 4505845,
                "message": "O valor do campo '{0}' nao pode ser '{1}', vazio ou null, utilize um valor do tipo array [\"a\", \"b\", 1, 2]"
            }
        }

    def addx(self, code, params):
        error = self.error_messages[code]
        self.add(error["code"], error["message"].format(*params))

    def add(self, code, message):
        self.has_error = True
        self.__list_errors.append(
            {"code": code, "message": message}
        )

    def add_required(self, code, message):
        self.has_error = True
        self.ready = False
        self.__list_errors.append(
            {"code": code, "message": message}
        )

    def add_field(self, field, value, code, message):
        self.has_error = True
        self.__list_errors.append(
            {"field": field, "code": code, "value": value, "message": message}
        )

    def add_field_required(self, field, code, message):
        self.has_error = True
        self.ready = False
        self.__list_errors.append(
            {"field": field, "code": code, "message": message}
        )

    def to_list(self):
        if len(self.__list_errors) > 0:
            return self.__list_errors
        return None
