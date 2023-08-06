#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bson
import time
import datetime
from pymongo import MongoClient
from datarest_db import DataRestDB
from datatypes import DataTypes
from status import Status


# TODO:: Implementar multi-idiomas classe ServiceDB
# TODO:: Implementar try catch para a criação do banco de dados mongo db
# TODO:: Refatorar classe ServiceDB
# TODO:: Implementar identificação de owner_id, last_owner_id, api_key, app_id, group
class ServiceDB:
    def __init__(self, message, mongo_ip, mongodb_port):

        # Conecta ao banco de dados
        self.mongo_server = MongoClient(mongo_ip, mongodb_port)
        self.status = Status()
        self.__data_types = DataTypes()
        self.__data_rest_db = DataRestDB(message, self.status)

        self.__action()

    # --------------------------------
    # find
    # --------------------------------
    # Realiza consulta na base de dados buscando um ou muitos documentos
    # TODO:: Implementar multi-idiomas classe ServiceDB::find
    # TODO:: Preparar filtro para ser retornado ao cliente
    # TODO:: Preparar fields ser retornado ao cliente
    # TODO:: Preparar conversão de dados ser retornado ao cliente (date, object_id, decimal)
    # TODO:: Implementar links de paginador
    def find(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera configurações
        db_fields = self.__data_rest_db.fields()
        db_filter = self.__data_rest_db.filter()
        db_limit = self.__data_rest_db.limit()
        db_offset = self.__data_rest_db.offset()
        db_sort = self.__data_rest_db.sort()

        # Consulta o banco de dados
        find_result = collection.find(db_filter, db_fields).skip(db_offset).sort(db_sort.items())
        finded_count = find_result.count()

        # Obtém o resultado da consulta
        find_result_limit = list(find_result.limit(db_limit))

        # Prepara os dados dos documentos recuperados $date, $timestamp ...
        find_result_limit, filtered_count = self.__prepare_result(find_result_limit)

        data_finded = {}
        # Prepara os resultados para serem retornados ao cliente
        if "item" == self.__data_rest_db.result_type():
            if filtered_count == 1:
                data_finded = find_result_limit[0]
            else:
                self.status.warn("WARN_FIND_ITEM", None, [])

        elif "list" == self.__data_rest_db.result_type():
            data_finded = find_result_limit

        if finded_count == 0:
            message = "Nenhum documento encontrado."
        elif finded_count == 1:
            message = "1 documento encontrado."
        else:
            message = self.__data_types.to_str(filtered_count) + " documentos encontrados."

        self.__data_rest_db.result({
            "success": True,
            "message": message,
            "data_finded": data_finded,
            "count": {
                "finded": finded_count,
                "filtered": filtered_count
            },
            "query": {
                "limit": db_limit,
                "offset": db_offset,
                "fields": db_fields,
                "filter": db_filter,
                "sort": db_sort
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
    # TODO:: Implementar multi-idiomas classe ServiceDB::insert
    def insert(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        db_data = self.__data_rest_db.data()
        db_fields = self.__data_rest_db.fields()

        # Verifica o tipo de dados
        if type(db_data) == dict and len(db_data.keys()) > 0:
            db_data = [db_data]

        data_inserted = {}
        # Verifica se tem dados para inseretir na base de dados
        if len(db_data) > 0:
            # Insere documentos na base de dados e recupera a lista dos identificadores dos documentos inseridos
            insert_many_result = collection.insert_many(db_data).inserted_ids

            # Verifica se algum documento foi inserido
            if len(insert_many_result) > 0:
                # Prepara filtro para recuperar lista de documentos inseridos
                db_filter = {"_id": {"$in": insert_many_result}}

                # Realiza consulta na base de dados e recupera a lista de documentos inseridos
                find_result = collection.find(db_filter, db_fields)

                # Prepara os dados dos documentos recuperados $date, $timestamp ...
                find_result, inserted_count = self.__prepare_result(find_result)

                # Prepara os resultados para serem retornados ao cliente
                if "item" == self.__data_rest_db.result_type():
                    if inserted_count == 1:
                        data_inserted = find_result[0]
                    elif inserted_count > 1:
                        data_inserted = find_result[0]
                        self.status.warn("WARN_INSERT_ITEM", None, [])

                elif "list" == self.__data_rest_db.result_type():
                    data_inserted = find_result

                if inserted_count == 1:
                    message = "1 documento foi inserido com sucesso."
                else:
                    message = self.__data_types.to_str(inserted_count) + " documentos inseridos com sucesso."

                # Prepara configurações que serão retornadas para o cliente
                self.__data_rest_db.result({
                    "success": True,
                    "message": message,
                    "data_inserted": data_inserted,
                    "count": {
                        "inserted": inserted_count
                    },
                    "query": {
                        "fields": db_fields
                    }
                })
        else:
            # Em case de erros por fata de documentos para inserir na base de dados ou qualquer outra falha no momento da inserção
            # registra mensagem de erro e configura a flha na operação
            self.status.error("NO_DATA_TO_INSERT", None, [])

            # Prepara os resultados para serem retornados ao cliente
            if "item" == self.__data_rest_db.result_type():
                data_inserted = {}
            else:
                data_inserted = []

            message = "Nenhum documento foi inserido."

            # Registra resultado que será retornado para o servidor rest
            self.__data_rest_db.result({
                "success": False,
                "message": message,
                "data_inserted": data_inserted,
                "count": {
                    "inserted": 0
                },
                "query": {
                    "fields": db_fields
                }
            })

    # --------------------------------
    # prepare_result_update
    # --------------------------------
    # TODO:: Refatorar classe ServiceDB:: prepare_result_update
    @staticmethod
    def prepare_result_update(data):
        list_scheme = ["$currentDate", "$inc", "$min", "$max", "$mul", "$rename", "$set", "$setOnInsert", "$unset"]
        data_update = {}
        for key in data:
            if key in list_scheme:
                for item in data[key]:
                    data_update[item] = data[key][item]

        return data_update

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.status.ready()

    # --------------------------------
    # remove
    # --------------------------------
    # Remove um ou muitos documentos na base de dados
    #
    # TODO:: Implementar solução final para tratar _ID
    # TODO:: Resolver problemas exclusão de um em usando $in, item/lista de ids em filtros in {'_id': {'$in': ObjectId('5aad1be48356691750d406c0')}}
    # TODO:: Implementar multi-idiomas classe ServiceDB::remove
    def remove(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        db_filter = self.__data_rest_db.filter()

        if "id" in db_filter.keys():
            db_filter["_id"] = bson.ObjectId(db_filter["id"]["$eq"])
            del db_filter["id"]

        # Realiza busca na colecção para recuperar documentos que serão atualizados
        find_result = collection.find(db_filter)
        find_result_count = find_result.count()

        # Verifica se existe documentos para serem atualizados
        deleted_count = 0
        deleted_ids = []
        if find_result_count > 0:
            # Recupera a coleção trash
            collection_trash = self.__collection_trash()

            # Grava os documentos localizados na coleção trash
            insert_data_trash, deleted_ids = self.__prepare_data_trash(find_result)
            insert_many_result = collection_trash.insert_many(insert_data_trash).inserted_ids

            # Verifica se foi inserido documento na coleção trash
            if len(insert_many_result) > 0:
                # Atualiza os documentos da coleção principal
                delete_result = collection.delete_many(db_filter)
                deleted_count = delete_result.deleted_count

                # Verifica se os documentos não foram atualizados
                if deleted_count == 0:
                    # Remove itens inseridos na tabela trash
                    collection_trash.delete_many({"_id": {"$in": insert_many_result}})

        if deleted_count == 0:
            message = "Nenhum documento foi removido."
        elif deleted_count == 1:
            message = "1 documento removido com sucesso."
        else:
            message = self.__data_types.to_str(deleted_count) + " documentos removidos com sucesso."

        # Prepara configurações que serão retornadas para o cliente
        self.__data_rest_db.result({
            "success": True,
            "message": message,
            "deleted_ids": deleted_ids,
            "count": {
                "deleted": deleted_count
            },
            "query": {
                "filter": db_filter
            },
            "info": {}
        })

    # --------------------------------
    # send
    # --------------------------------
    def send(self):
        return self.__data_rest_db.send()

    # --------------------------------
    # update
    # --------------------------------
    # TODO:: Implementar multi-idiomas classe ServiceDB::update
    def update(self):
        # Recupera a coleção principal
        collection = self.__collection()

        # Recupera dados e configurações
        db_data = self.__data_rest_db.data()
        db_fields = self.__data_rest_db.fields()
        db_filter = self.__data_rest_db.filter()

        # Realiza busca na colecção para recuperar documentos que serão atualizados
        find_result = collection.find(db_filter, db_fields)
        find_result_count = find_result.count()

        # Verifica se existe documentos para serem atualizados
        update_count = 0
        if find_result_count > 0:
            # Recupera a coleção changes
            collection_changes = self.__collection_changes()

            # Grava os documentos localizados na coleção trash
            insert_result = collection_changes.insert(self.__prepare_data_changes(db_data, find_result), check_keys=False)

            # Verifica se foi inserido documento na coleção _changes
            if insert_result:
                # Atualiza os documentos da coleção principal
                update_result = collection.update_many(db_filter, db_data, upsert=True)
                update_count = update_result.modified_count

                # Verifica se os documentos não foram atualizados
                if update_count == 0:
                    # Remove itens inseridos na tabela change
                    collection_changes.delete_one({"_id": insert_result})

        # Prepara os dados dos documentos recuperados $date, $timestamp ...
        update_result = self.prepare_result_update(db_data)

        data_updated = {}
        # Prepara os resultados para serem retornados ao cliente
        if "item" == self.__data_rest_db.result_type():
            if update_count == 1:
                data_updated = update_result
            elif update_count > 1:
                data_updated = update_result[0]

        elif "list" == self.__data_rest_db.result_type():
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
        self.__data_rest_db.result({
            "success": True,
            "message": message,
            "data_updated": data_updated,
            "count": {
                "modified": update_count
            },
            "query": {
                "fields": db_fields,
                "filter": db_filter
            }
        })

    # --------------------------------
    # __action
    # --------------------------------
    def __action(self):
        action = self.__data_rest_db.action()
        if hasattr(self, action):
            method = getattr(self, action)
            method()
        else:
            self.status.error("INVALID_ACTION_DB", None, [action])

    # --------------------------------
    # __collection
    # --------------------------------
    # Recupera instancia da coleção que receberá interação na base de dados
    # TODO:: Verificar se o banco de dados esta instanciado antes de tentar criar a coleção
    def __collection(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__data_rest_db.database()]
        # Recupera/Cria a coleção mongo db
        return database[self.__data_rest_db.collection()]

    # --------------------------------
    # __collection_changes
    # --------------------------------
    def __collection_changes(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__data_rest_db.database()]
        # Recupera/Cria a coleção mongo db
        return database["_changes"]

    # --------------------------------
    # __collection_trash
    # --------------------------------
    def __collection_trash(self):
        # Recupera o banco de dados mongo db
        database = self.mongo_server[self.__data_rest_db.database()]
        # Recupera/Cria a coleção mongo db
        return database["_trash"]

    # --------------------------------
    # __prepare_data_changes
    # --------------------------------
    # TODO:: Refatorar classe ServiceDB:: __prepare_data_changes
    def __prepare_data_changes(self, data_update, data_active):
        data_active = list(data_active)

        def get(d, keys):
            if "." in keys:
                k, rest = keys.split(".", 1)
                if k in d.keys():
                    return get(d[k], rest)
                return "__undefined__"
            else:
                if keys in d.keys():
                    return d[keys]
                return "__undefined__"

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

        insert_data_update = {
            "filter": {},
            "data": data,
            "created_time": self.__data_types.to_str(datetime.datetime.utcnow()),
            "owner_id": "5aa73a758356693ffc73499c",
            "collection": self.__data_rest_db.collection()
        }

        return insert_data_update, data

    # --------------------------------
    # __prepare_data_trash
    # --------------------------------
    # TODO:: Refatorar classe ServiceDB:: __prepare_data_trash
    def __prepare_data_trash(self, data):
        # Retirar list de ids que foram removidos da base de dados
        deleted_ids = []
        insert_data_trash = []

        for item in data:
            deleted_ids.append(self.__data_types.to_str(item["_id"]))
            insert_data_trash.append({
                "data": item,
                "created_time": self.__data_types.to_str(datetime.datetime.utcnow()),
                "owner_id": "5aa73a758356693ffc73499c",
                "collection": self.__data_rest_db.collection()
            })
        return insert_data_trash, deleted_ids

    # --------------------------------
    # __prepare_result
    # --------------------------------
    # TODO:: Refatorar classe ServiceDB:: __prepare_result
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
                    # format = "%a %b %d %H:%M:%S %Y"
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

        final_result = list(map(action, data))
        return final_result, len(final_result)
