#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bson.int64 import Int64
from devdoo.datarest import DataRest
from devdoo.database import DataBase
from datatypes import DataTypes

class Service(object):
    def __init__(self, message, id, name, schemes, actions, custom_service=None):
        self.__data_types = DataTypes()
        self.actions = actions
        self.id = id
        self.name = name
        self.schemes = schemes

        self.__database = DataBase()
        self.__datarest = DataRest(message, custom_service)

    # ----------------------------------------------------------------
    #
    # Public Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        source = self.__datarest.source()
        method = self.__datarest.method()

        print "SOURCE", source
        print "METHOD", method

        # Verifica se o endereço da api existe
        if source in self.actions[method].keys():
            # Recupera o objeto de configuração da api
            service_api = self.actions[method][source]
            action = service_api["action"]
            self.__datarest.result_type(action["result_type"])

            if hasattr(self, action["database_action"]) and self.__datarest.validate_service(self.name, self.id):
                method = getattr(self, action["database_action"])
                if action["database_action"] == "update":
                    method(action["collection"], action["scheme"], self.schemes)
                else:
                    method(action["collection"], self.__get_scheme(action["scheme"], self.schemes), self.__get_max_limit(action))
            else:
                # TODO:: Melhorrar mensagem de erro para API INVALIDA E ACAO INVALIDA
                # TODO:: Informar na mensagem de erro que o id não  valido
                self.__datarest.add_error_required("AAA ACTION INVALIDA",
                                                   source + " :: action nao existe no servico '" + self.name + "' da versao::" + " " +
                                                   self.__data_types.to_str(service_api["action"]) + "metodo::" + method)
        else:
            self.__datarest.add_error_required("BBB API INVALIDA", source + ":: endpoint da api nao existe no servico " + self.name + " da versao::"+ "metodo::" + method)

    def __get_scheme(self, scheme, list_schemes):
        result = {}
        for field_name in scheme:
            if field_name in list_schemes.keys():
                result[field_name] = list_schemes[field_name]
            else:
                self.__datarest.add_error_required("NOME DO CAMPO API não registrado--->>>", field_name)
        return result

    def __get_max_limit(self, action):
        if "max_limit" in action:
            return action["max_limit"]
        return None

    # --------------------------------
    # insert
    # --------------------------------
    # Prepara documento para ser inserido base de dados
    def insert(self, collection, list_scheme, max_limit=None):
        list_save_data = []

        # Define o tipo de ação que será executada no servidor de base de dados
        self.__datarest.action("insert")

        # Recupera o identificador da coleção
        self.__datarest.collection(collection)

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean, body_field_errors, dev_fields_errors = self.__database.fields_save(self.__datarest.body, list_scheme)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o equema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser insrido na base de dados
            field_name, field_value = self.__datarest.validate_field_save(item_scheme_name, item_scheme, field_value, "custom_save")

            # Verifica se o campo não está com erro de validação
            if field_value != '__error__' and field_value != '__ERROR__':
                # Registra o campo na lista de dados que deverá ser enviada para o servidor de base de dados
                if field_name != "id":
                    list_save_data.append({"field": field_name, "value": field_value})

        # Prepara s lista de campos que será enviada para o servidor de base de dados
        # Prepara a lista de campos que devrá ser retornada do servidor depois de salvar na base de dados
        list_save_data = self.__prepare_save_data_fields(list_save_data)

        # Registra os dados do documento
        self.__datarest.data(list_save_data)

        # Registra as datas de criação e alteração do documento
        self.__datarest.created_time()
        self.__datarest.changed_time()

        # Caso o campo nao esteja registrado no scheme, registra mensagem de error
        for item_field_name in body_field_errors:
            self.__datarest.add_error(125489, "O campo '" + item_field_name + "' nao existe.")

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.__datarest.add_error_required(362548,
                                               "DEV ERROR O campo '" + item_field_name + "' nao pode ser utilizado por existir campos filhos.")

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_save_data) <= 0:
            self.__datarest.add_error_required(85545454, "Nao tem nada para gravar no banco de dados")

    # --------------------------------
    # find
    # --------------------------------
    def find(self, collection, list_scheme, max_limit=None):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.__datarest.action("find")

        # Recupera o identificador da coleção
        self.__datarest.collection(collection)

        # Prepara a lista de campos válidos que poderão ser recuperados na base de dados
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        fields, dev_fields_errors = self.__database.fields_find(list_scheme)

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.__datarest.add_error_required(362548,
                                               "DEV ERROR O campo '" + item_field_name + "' nao pode ser utilizado por existir campos filhos.")

        # Registra campos que devem ser retornados
        self.__datarest.fields(fields)
        self.__datarest.limit(max_limit)

        # self.__order() #TODO:: Implementar Order
        # self.__cursor() #TODO:: Implementar Cursors

    # --------------------------------
    # remove
    # --------------------------------
    def remove(self, collection, list_scheme, max_limit=None):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.__datarest.action("remove")

        # Recupera o identificador da coleção
        self.__datarest.collection(collection)

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.__datarest.ready()

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        return self.__datarest.send_database()

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        return self.__datarest.send_error()

    # --------------------------------
    # update
    # --------------------------------
    def update(self, collection, scheme, list_scheme):
        #Validar configuração de schema para update, erro developer
        if self.__is_valid_scheme(scheme):
            # Define o tipo de ação que será executada no servidor de base de dados
            self.__datarest.action("update")

            # Recupera o identificador da coleção
            self.__datarest.collection(collection)

            update_data = {}
            fields = ["_id"]
            for item_scheme in scheme:
                obj_item_scheme = self.__get_scheme(scheme[item_scheme], list_scheme)
                obj_item_scheme = self.update_config(obj_item_scheme)

                if len(obj_item_scheme.keys()) > 0:
                    fields = fields + obj_item_scheme.keys()
                    update_data[item_scheme] = obj_item_scheme

            # Registra os dados do documento
            self.__datarest.data(update_data)

            # Registra campos que devem ser retornados
            self.__datarest.fields(fields)

            # Registra as datas de criação e alteração do documento
            self.__datarest.changed_time()

            # Verificar se tem algo para gravar no banco
            if len(update_data.keys()) <= 0:
                self.__datarest.add_error_required(85545454, "Nao tem nada para ATUALIZAR no banco de dados")
        else:
            self.__datarest.add_error_required(54554854, "Esquema de update Inválido não encontrado $set, $inc...")

    # --------------------------------
    # update_config
    # --------------------------------
    # TODO:: implementar checksum de update
    def update_config(self, list_scheme):

        list_update_data = []

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean, body_field_errors, dev_fields_errors = self.__database.fields_update(self.__datarest.body, list_scheme)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o equema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser inserido na base de dados
            field_name, field_value = self.__datarest.validate_field_update(item_scheme_name, item_scheme, field_value, "custom_update")

            # Verifica se o campo não está com erro de validação
            if field_value != '__error__' and field_value != '__ERROR__':
                # Registra o campo na lista de dados que deverá ser enviada para o servidor de base de dados
                if field_name != "id":
                    list_update_data.append({"field": field_name, "value": field_value})

        # Prepara a lista de campos que será enviada para o servidor de base de dados
        # Prepara a lista de campos que devrá ser retornada do servidor depois de salvar na base de dados
        list_update_data = self.__prepare_update_data(list_update_data)

        # Caso o campo nao esteja registrado no scheme, registra mensagem de error
        for item_field_name in body_field_errors:
            self.__datarest.add_error(125489, "O campo '" + item_field_name + "' nao existe.")

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.__datarest.add_error_required(362548,
                                               "DEV ERROR O campo '" + item_field_name + "' nao pode ser utilizado por existir campos filhos.")

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_update_data) <= 0:
            self.__datarest.add_error_required(85545454, "Nao tem nada para atualizar no banco de dados")

        return list_update_data

    # --------------------------------
    # __prepare_save_data_fields
    # --------------------------------
    # Prepara lista de campos que podem ser incluidos no documento
    # Prepara e registra a lista de campos que deverá ser retornada do servidor após a inclusão do documento na base de dados
    def __prepare_save_data_fields(self, list_data):
        result = {}
        fields = {}

        for item in list_data:
            # Verifica se o nome do campo existe na lista que será incluida no documento
            if (item["field"]) in result.keys():
                # Caso não esteja na lista então o campo é incluido
                # Prepara objetos filhos no padrão permitido paraga registrar na base de dados
                result[(item["field"])] = self.__save_data_join(result[(item["field"])], item["value"])
            else:
                # Registra o campo e valor na lista de campos válida do documento
                result[(item["field"])] = item["value"]

            # Adiciona o campo na lista de campos que devem ser retornados do servidor
            fields[(item["field"])] = True

        # Registra campos que devem ser retornados
        self.__datarest.fields(fields)

        return result


    def __is_valid_scheme(self, scheme):
        if type(scheme) == dict:
            list_scheme = ["$currentDate", "$inc", "$min", "$max", "$mul", "$rename", "$set", "$setOnInsert", "$unset"]
            for key in scheme.keys():
                if key in list_scheme:
                    return True
        return False

    # --------------------------------
    # __prepare_update_data
    # --------------------------------
    # Prepara lista de campos que podem ser atualizados no documento
    def __prepare_update_data(self, list_data):
        result = {}
        for item in list_data:
            # Registra o campo e valor na lista de campos válida do documento
            result[(item["field"])] = item["value"]
        return result

    # --------------------------------
    # __save_data_join
    # --------------------------------
    # Função recursiva utilizada para tratar conflito de elementos filho no momento de gravar na base de dados
    #
    # data - Objeto contento dados existentes do mesmo grupo ou um objeto vazio para receber novos elementos
    # value - Dados que deverão ser inseridos no objeto
    def __save_data_join(self, data, value):

        # Pega cada elemento do objeto valor
        for item in value:
            # Verifica se valor é um objeto
            # Verifica se o elemento filho valor é um objeto
            # Verifica se o elemento filho existe no objeto de dados
            if type(value) == dict and type(value[item]) == dict and type(data) == dict and item in data.keys():
                # Adiciona novo elemento no objeto de dados com o resultado da interação nos objetos filhos do objeto valor
                data[item] = self.__save_data_join(data[item], value[item])

            # Verifica se valor é um objeto
            # Verifica se o elemento filho valor é um objeto
            elif type(value) == dict and type(data) == dict:
                # Adiciona o objeto valor como novo elemento no objeto de dados
                data[item] = value[item]

            # Verifica se o objeto dados é um objeto
            elif type(data) == dict:
                # Adiciona o valor como novo elemento no objeto de dados
                data[item] = value
        return data
