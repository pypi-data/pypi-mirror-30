#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bson, time, datetime
from pymongo import MongoClient
from datarest_db import DataRest_DB
from datatypes import DataTypes


class Service_DB():
    def __init__(self, message, mongo_ip, mongodb_port):
        self.__data_types = DataTypes()
        # Conecta ao banco de dados
        self.mongo_server = MongoClient(mongo_ip, mongodb_port)
        self.__datarest = DataRest_DB(message)
        self.action()

    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        action = self.__datarest.action()
        if hasattr(self, action):
            method = getattr(self, action)
            method()
        else:
            self.__datarest.add_error("ACTION ERRADA - MONGO DB", action + ":: action nao existe no servico")

    def send(self):
        return self.__datarest.send()

    # ----------------------------------------------------------------
    #
    # Public Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # find
    # --------------------------------
    # Realiza consulta na base de dados buscando um ou muitos documentos
    def find(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera configurações
        fields = self.__datarest.fields()
        filter = self.__datarest.filter()
        limit = self.__datarest.limit()
        offset = self.__datarest.offset()
        sort = self.__datarest.sort()

        # Consulta o banco de dados
        find_result = collection.find(filter, fields).skip(offset).sort(sort.items())
        finded_count = find_result.count()

        # Obtém o resultado da consulta
        find_result_limit = list(find_result.limit(limit))

        # Prepara os dados dos documentos recuperados $date, $timestamp ...
        find_result_limit, filtered_count = self.__prepare_result(find_result_limit)

        # Prepara os resultados para serem retornados ao cliente
        if "item" == self.__datarest.result_type():

            print "FIND", list(find_result_limit)

            data_finded = {}
            if filtered_count == 1:
                data_finded = find_result_limit[0]
            else:
                self.__datarest.add_error("ERROR FIND - ITEM",
                                          "O filtro da busca encontrou mais mais itens do que o esperado, nenhum item é retornado")
        elif "list" == self.__datarest.result_type():
            data_finded = find_result_limit

        if finded_count == 0:
            message = "Nenhum documento encontrado."
        elif finded_count == 1:
            message = "1 documento encontrado."
        else:
            message = self.__data_types.to_str(filtered_count) + " documentos encontrados."

        self.__datarest.result({
            "success": True,
            "message": message,
            "data_finded": data_finded,
            "count": {
                "finded": finded_count,
                "filtered": filtered_count
            },
            "query": {
                "limit": limit,
                "offset": offset,
                "fields": fields,
                "filter": filter  # TODO: Preparar filtro para ser retornado ao cliente
            },
            "links": {
                "previous": None,
                "next": "https://api.predicthq.com/v1/endpoint/?offset=10&limit=10"
            }
        })

    # --------------------------------
    # insert
    # --------------------------------
    # Insere um ou muitos documentos na base de dados
    def insert(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        data = self.__datarest.data()
        fields = self.__datarest.fields()
        filter = self.__datarest.filter()

        # Verifica o tipo de dados
        if type(data) == dict and len(data.keys()) > 0:
            data = [data]

        # Verifica se tem dados para inseretir na base de dados
        if len(data) > 0:
            # Insere documentos na base de dados e recupera a lista dos identificadores dos documentos inseridos
            insert_many_result = collection.insert_many(data).inserted_ids

            # Verifica se algum documento foi inserido
            if len(insert_many_result) > 0:
                # Prepara filtro para recuperar lista de documentos inseridos
                filter = {"_id": {"$in": insert_many_result}}

                # Realiza consulta na base de dados e recupera a lista de documentos inseridos
                find_result = collection.find(filter, fields)

                # Prepara os dados dos documentos recuperados $date, $timestamp ...
                find_result, inserted_count = self.__prepare_result(find_result)

                # Prepara os resultados para serem retornados ao cliente
                if "item" == self.__datarest.result_type():
                    data_inserted = {}
                    if inserted_count == 1:
                        data_inserted = find_result[0]
                    elif inserted_count > 1:
                        data_inserted = find_result[0]

                        # TODO:: Mudar mensagem de erro para warning
                        self.__datarest.add_error("ERROR ISERT - ITEM",
                                                  "Muitos documentos foram inseridos utilizando um endpoit do tipo 'item', somente o primeiro documento é retornado")
                elif "list" == self.__datarest.result_type():
                    data_inserted = find_result

                if inserted_count == 1:
                    message = "1 documento foi inserido com sucesso."
                else:
                    message = self.__data_types.to_str(inserted_count) + " documentos inseridos com sucesso."

                # Prepara configurações que serão retornadas para o cliente
                self.__datarest.result({
                    "success": True,
                    "message": message,
                    "data_inserted": data_inserted,
                    "count": {
                        "inserted": inserted_count
                    },
                    "query": {
                        "fields": fields,
                        "filter": filter  # TODO: Preparar filtro para ser retornado ao cliente
                    }
                })
        else:
            # Em case de erros por fata de documentos para inserir na base de dados ou qualquer outra falha no momento da inserção
            # registra mensagem de erro e configura a flha na operação
            self.__datarest.add_error(485752, "Não tem documentos para inserir na base de dados")

            # Prepara os resultados para serem retornados ao cliente
            if "item" == self.__datarest.result_type():
                data_inserted = {}
            else:
                data_inserted = []

            message = "Nenhum documento foi inserido."

            # Registra resultado que será retornado para o servidor rest
            self.__datarest.result({
                "success": False,
                "message": message,
                "data_inserted": data_inserted,
                "count": {
                    "inserted": 0
                },
                "query": {
                    "fields": fields,
                    "filter": filter  # TODO: Preparar filtro para ser retornado ao cliente
                }
            })

    # --------------------------------
    # update
    # --------------------------------
    def update(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        data = self.__datarest.data()
        fields = self.__datarest.fields()
        filter = self.__datarest.filter()

        # TODO:: UPDATE - Verificar se existe filtro definido

        # Realiza busca na colecção para recuperar documentos que serão atualizados
        find_result = collection.find(filter, fields)
        find_result_count = find_result.count()

        # Verifica se existe documentos para serem atualizados
        update_count = 0
        if find_result_count > 0:
            # Recupera a coleção changes
            collection_changes = self.__collection_changes()

            # Grava os documentos localizados na coleção trash
            insert_result = collection_changes.insert(self.__prepare_data_changes(data, find_result), check_keys=False)

            # Verifica se foi inserido documento na coleção _changes
            if insert_result:
                # Atualiza os documentos da coleção principal
                update_result = collection.update_many(filter, data, upsert=True)
                update_count = update_result.modified_count

                # Verifica se os documentos não foram atualizados
                if update_count == 0:
                    # Remove itens inseridos na tabela change
                    delete_result = collection_changes.delete_one({"_id": insert_result})

        # Prepara os dados dos documentos recuperados $date, $timestamp ...
        update_result = self.__prepare_result_update(data)

        # Prepara os resultados para serem retornados ao cliente
        if "item" == self.__datarest.result_type():
            data_updated = {}
            if update_count == 1:
                data_updated = update_result
            elif update_count > 1:
                data_updated = update_result[0]

        elif "list" == self.__datarest.result_type():
            data_updated = update_result
            if type(update_result) == dict:
                data_updated = [update_result]

        if update_count == 0:
            message = "Nenhum documento foi atualizado."
        elif update_count == 1:
            message = "1 documento atualizado com sucesso."
        else:
            message = self.__data_types.to_str(update_count) + " documentos atualizados com sucesso."

        # Prepara configurações que serão retornadas para o cliente
        self.__datarest.result({
            "success": True,
            "message": message,
            "data_updated": data_updated,
            "count": {
                "modified": update_count
            },
            "query": {
                "fields": fields,
                "filter": filter
            }
        })

    # --------------------------------
    # remove
    # --------------------------------
    # Remove um ou muitos documentos na base de dados
    #
    def remove(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        data = self.__datarest.data()
        filter = self.__datarest.filter()

        # TODO:: Implementar solição final para tratar _ID
        # TODO:: Resolver problemas exclusão de um em usando $in, item/lista de ids em filtros in {'_id': {'$in': ObjectId('5aad1be48356691750d406c0')}}
        if "id" in filter.keys():
            filter["_id"] = bson.ObjectId(filter["id"]["$eq"])
            del filter["id"]

        # TODO:: DELETE - Verificar se existe filtro definido

        # Realiza busca na colecção para recuperar documentos que serão atualizados
        find_result = collection.find(filter)
        find_result_count = 0
        find_result_count = find_result.count()

        # Verifica se existe documentos para serem atualizados
        deleted_count = 0
        deleted_ids = []
        if find_result_count > 0:
            # Recupera a coleção trash
            collection_trash = self.__collection_trash()

            # Grava os documentos localizados na coleção trash
            save_data_trash, deleted_ids = self.__prepare_data_trash(find_result)
            insert_many_result = collection_trash.insert_many(save_data_trash).inserted_ids

            # Verifica se foi inserido documento na coleção trash
            if len(insert_many_result) > 0:
                # Atualiza os documentos da coleção principal
                delete_result = collection.delete_many(filter)
                deleted_count = delete_result.deleted_count

                # Verifica se os documentos não foram atualizados
                if deleted_count == 0:
                    # Remove itens inseridos na tabela trash
                    delete_result = collection_trash.delete_many({"_id": {"$in": insert_many_result}})

        # TODO:: Implementar multi-idiomas
        if deleted_count == 0:
            message = "Nenhum documento foi removido."
        elif deleted_count == 1:
            message = "1 documento removido com sucesso."
        else:
            message = self.__data_types.to_str(deleted_count) + " documentos removidos com sucesso."

        # Prepara configurações que serão retornadas para o cliente
        self.__datarest.result({
            "success": True,
            "message": message,
            "deleted_ids": deleted_ids,
            "count": {
                "deleted": deleted_count
            },
            "query": {
                "filter": filter
            },
            "info": {}
        })

    # ----------------------------------------------------------------
    #
    # Private Methods
    #
    # ----------------------------------------------------------------
    # --------------------------------
    # __collection
    # --------------------------------
    # Recupera instancia da coleção que receberá interação na base de dados
    def __collection(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__datarest.database()]
        # Recupera/Cria a coleção mongo db
        return database[self.__datarest.collection()]

    def __collection_trash(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__datarest.database()]
        # Recupera/Cria a coleção mongo db
        return database["_trash"]

    def __collection_changes(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__datarest.database()]
        # Recupera/Cria a coleção mongo db
        return database["_changes"]

    def __prepare_data_changes(self, data_update, data_active):

        data_active = list(data_active)

        def get(d, keys):
            if "." in keys:
                key, rest = keys.split(".", 1)
                if key in d.keys():
                    return get(d[key], rest)
                return "__undefined__"
            else:
                if keys in d.keys():
                    return d[keys]
                return "__undefined__"

        save_data_update = []
        documents = {}
        # gupos de interação $set, $inc ...
        for item in data_update:

            # itens de cada grupo
            for data_item in data_update[item]:
                # itens dos documento da base de dados
                for item_find in data_active:
                    active_id = item_find["_id"]

                    if active_id not in documents.keys():
                        documents[active_id] = {
                            "change_data_active": [],
                            "change_data_update": []
                        }

                    value_update = data_update[item][data_item]
                    value_active = get(item_find, data_item)
                    if value_active != value_update:
                        if value_active != "__undefined__":
                            active = {}
                            active[data_item] = value_active
                            (documents[active_id]["change_data_active"]).append(active)

                        update = {}
                        update[data_item] = value_update
                        (documents[active_id]["change_data_update"]).append(update)

        data = {}

        for id_doc in documents:
            doc_active = {}
            list_data_active = documents[id_doc]["change_data_active"]
            for item_data_active in list_data_active:
                key = item_data_active.keys()
                doc_active[(key[0])] = item_data_active[(key[0])]
            if len(doc_active.keys()) > 0:
                if self.__data_types.to_str(id_doc) not in data:
                    data[self.__data_types.to_str(id_doc)] = {}
                data[self.__data_types.to_str(id_doc)]["active"] = doc_active

            doc_update = {}
            list_data_update = documents[id_doc]["change_data_update"]
            for item_data_update in list_data_update:
                key = item_data_update.keys()
                doc_update[(key[0])] = item_data_update[(key[0])]
            if len(doc_update.keys()) > 0:
                if self.__data_types.to_str(id_doc) not in data:
                    data[self.__data_types.to_str(id_doc)] = {}
                data[self.__data_types.to_str(id_doc)]["update"] = doc_update

        save_data_update = {
            "filter": {},
            "data": data,
            "created_time": self.__data_types.to_str(datetime.datetime.utcnow()),
            "owner_id": "5aa73a758356693ffc73499c",
            "collection": self.__datarest.collection()
        }

        return save_data_update, data

    def __obj_to_dot_value(self, data):
        result = {}

        # Converte objetos em dot_string parametros
        def dot(d, dot_list):
            keys = d.keys()
            k = keys[0]
            dot_list.append(k)
            # Verificar se existe elementos filhos
            if type(d[k]) == dict and d[k].keys() > 0:
                return dot(d[k], dot_list)
            elif type(d) == dict and d.keys() > 0:
                k = d.keys()[0]
                return d[k]

        for item in data:
            if type(data[item]) == dict:
                dot_list = [item]
            else:
                result[item] = data[item]

        return result

    def __prepare_data_trash(self, data):
        # Retirar list de ids que foram removidos da base de dados
        deleted_ids = []
        save_data_trash = []

        for item in data:
            deleted_ids.append(self.__data_types.to_str(item["_id"]))
            save_data_trash.append({
                "data": item,
                "created_time": self.__data_types.to_str(datetime.datetime.utcnow()),
                "owner_id": "5aa73a758356693ffc73499c",
                "collection": self.__datarest.collection()
            })
        return save_data_trash, deleted_ids

    # --------------------------------
    # __fields
    # --------------------------------
    def __fields(self, query_fields):
        list_fields = []

        for item_field in query_fields:
            if query_fields[item_field] == True:
                list_fields.append(item_field)
        return list_fields

    # --------------------------------
    # __prepare_result
    # --------------------------------
    def __prepare_result(self, data):
        def action(item_result):
            result = {}
            for item_field in item_result:
                # Converte ObjectId para string
                if type(item_result[item_field]) == bson.ObjectId:
                    if "_id" == item_field:
                        result['id'] = self.__data_types.to_str(item_result[item_field])
                    else:
                        result[item_field] = self.__data_types.to_str(item_result[item_field])

                # datetime.datetime
                # Converte datetime
                elif type(item_result[item_field]) == datetime.datetime:
                    format = "%a %b %d %H:%M:%S %Y"
                    result[item_field] = (item_result[item_field]).isoformat()

                # Converte Decimal128 para Float
                elif type(item_result[item_field]) == bson.decimal128.Decimal128:
                    result[item_field] = float(self.__data_types.to_str(item_result[item_field]))

                # TODO:: Estudar datas do Python:  https://docs.python.org/2/library/datetime.html
                # TODO:: Extrair timestamp no horário correto
                # Converte Timestamp para number
                elif type(item_result[item_field]) == bson.timestamp.Timestamp:
                    result[item_field] = time.mktime((item_result[item_field]).as_datetime().timetuple())
                    # datetime.timestamp() === 1234567890   time.time()
                    # datetime.isoformat(sep='T', timespec='auto') === YYYY-MM-DDTHH:MM:SS.mmmmmm
                else:
                    result[item_field] = item_result[item_field]

            return result

        result = list(map(action, data))
        return result, len(result)

    # --------------------------------
    # __prepare_result_update
    # --------------------------------
    def __prepare_result_update(self, data):
        list_scheme = ["$currentDate", "$inc", "$min", "$max", "$mul", "$rename", "$set", "$setOnInsert", "$unset"]
        data_update = {}
        for key in data:
            if key in list_scheme:
                for item in data[key]:
                    data_update[item] = data[key][item]

        return data_update
