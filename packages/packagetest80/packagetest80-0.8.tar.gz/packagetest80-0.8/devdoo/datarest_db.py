#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.json_util import dumps
from bson.json_util import loads


class DataRestDB:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, message, status):
        self.__action = None
        self.__collection = None
        self.__connection_id = None
        self.__data = {}
        self.__data_base = None
        self.__fields = []
        self.__result_type = None
        self.__sort = {}
        self.__service_id = None
        self.__info = {}
        self.__filter = {}
        self.__limit = 0
        self.__offset = 0
        self.__message_send = {}
        self.__method = None
        self.__token = None

        self.status = status
        self.decode(message)

    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        return self.__action

    # --------------------------------
    # collection
    # --------------------------------
    def collection(self):
        return self.__collection

    # --------------------------------
    # data
    # --------------------------------
    def data(self):
        return self.__data

    # --------------------------------
    # database
    # --------------------------------
    def database(self):
        return self.__data_base

    # --------------------------------
    # decode
    # --------------------------------
    # TODO:: Verificar todas as entradas de dados, confirmar tipagem esperada
    # TODO:: Implementar configurações do info de documento
    def decode(self, message):
        # Prepara o pacote a ser enviado
        json = loads(message)

        print "DECODE DB---->>>", json

        self.__action = json["action"]
        self.__collection = json["collection"]
        self.__connection_id = json["connection_id"]
        self.__data = json["data"]
        self.__data_base = json["database"]
        self.__fields = json["fields"]
        self.__result_type = json["result_type"]
        self.__sort = json["sort"]
        self.__service_id = json["service_id"]
        self.__info = json["info"]
        self.__filter = json["filter"]
        self.__limit = json["limit"]
        self.__offset = json["offset"]
        self.__method = json["method"]
        # self.__token = json["token"]
        self.status.add_errors(json["errors"])

    # --------------------------------
    # fields
    # --------------------------------
    def fields(self):
        return self.__fields

    # --------------------------------
    # filter
    # --------------------------------
    def filter(self):
        return self.__filter

    # --------------------------------
    # info
    # --------------------------------
    def info(self):
        return {
            "owner": {
                "id": self.__token,
                "last_id": self.__token
            }
        }

    # --------------------------------
    # limit
    # --------------------------------
    def limit(self):
        return self.__limit

    # --------------------------------
    # offset
    # --------------------------------
    def offset(self):
        return self.__offset

    # --------------------------------
    # result
    # --------------------------------
    # TODO:: Melhorar formato de dados retornados ao cliente
    def result(self, message):
        message["elapsed_time"] = {"response": "17.000", "server": "7.000"}
        message["method"] = self.__method

        if self.status.has_error():
            message["errors"] = self.status.to_list()

        self.__message_send = message

    # --------------------------------
    # result_type
    # --------------------------------
    def result_type(self):
        return self.__result_type

    # --------------------------------
    # send
    # --------------------------------
    # TODO:: Verificar se os dados para serem enviados ao cliente estão dentro das especificações esperadas
    # TODO:: Implementar sistema de gestão de consumo, analitico, histórico e log
    def send(self):
        # Registrar no stack de log
        # Registrar no stack de analytic
        # Registrar no stack de error
        # Registrar no stack de history
        # self.analyric.add({})

        return dumps({
            "connection_id": self.__connection_id,
            "message": self.__message_send
        })

    # --------------------------------
    # send_error
    # --------------------------------
    # TODO:: Melhorar mensagem de retorno em caso de falha
    def send_error(self):
        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps({
            "connection_id": self.__connection_id,
            "errors": self.status.to_list()
        })

    # --------------------------------
    # sort
    # --------------------------------
    def sort(self):
        return self.__sort
