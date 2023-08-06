#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
import hashlib
from bson.json_util import dumps
from bson.json_util import loads
from validate import Validate
from datafilter import DataFilter
from datatypes import DataTypes
from decode_types import DecodeTypes


# TODO:: Refatorar completamente a classe DataRest
# TODO:: Implementar configuração de limites definido no console para o serviço
class DataRest:
    def __init__(self, message, custom_service, status):

        self.status = status

        # self.action = None
        self.database_id = None
        self.database_name = None
        self.collection_name = None
        self.body = None
        # self.data = {}
        # self.fields = []
        self.filter = {}
        self.group = None
        self.id = None
        # self.info = None
        # self.limit = 0
        self.query = None
        self.service = None
        self.service_id = None
        self.token = None
        self.version = None

        self.__action = None
        self.__data_base = None
        self.__data_base_id = None
        self.__changed_time = 0
        self.__checksum = None
        self.__collection = None
        self.__connection_id = None
        self.__created_time = 0
        self.__data = {}
        self.__data_types = DataTypes()
        self.__default_limit = 100
        self.__fields = []
        self.__info = {}
        self.__filter = None
        self.__limit = 0
        self.__max_limit = 200
        self.__method = None
        self.__offset = 0
        self.__regex = None
        self.__result_type = None
        self.__search = None
        self.__service = None
        self.__service_id = None
        self.__sort = None
        self.__source = None
        self.__token = None
        self.__version = None

        self.validate = Validate(custom_service, self.status)
        self.decode_type = DecodeTypes(self.status)
        self.decode(message)

    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        return self.__action

    # --------------------------------
    # action_db
    # --------------------------------
    def action_db(self, action):
        self.__action = action

    # --------------------------------
    # changed_time
    # --------------------------------
    # TODO:: Implementar nos documentos atualizados
    def changed_time(self):
        self.__changed_time = self.__data_types.to_str(datetime.datetime.utcnow())

    # --------------------------------
    # checksum
    # --------------------------------
    # TODO:: Implementar checksum no docuemntos para insert e update
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

    def data(self, data):
        self.__data = data
        # Registra o checksum do documento
        self.checksum(data)

    # --------------------------------
    # decode_service
    # --------------------------------
    # TODO:: Mudar sistema de error, tirar de dentro do validate
    # TODO:: Mudar regra de criação de nomes de banco de dados
    def decode(self, message):
        # Prepara o pacote a ser enviado
        json = loads(message)

        self.body = json["body"]

        self.__action = self.decode_type.action(json["action"])
        self.__connection_id = self.decode_type.connection_id(json["connection_id"])
        self.__fields = json["fields"]
        self.__filter = DataFilter(json["filter"], self.status)
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

        self.__data_base_id = self.__service_id + 20000
        # self.group = self.info["application"]["group"]
        self.__data_base = "db" + self.__data_types.to_str(self.__data_base_id) + self.__service
        # self.info["database"] = {"name": self.database_name, "collection": None}

    # --------------------------------
    # field_insert
    # --------------------------------
    def field_insert(self, item_scheme_name, item_scheme, value, action=None):
        return self.validate.field_insert(item_scheme_name, item_scheme, value, action)

    # --------------------------------
    # field_update
    # --------------------------------
    def field_update(self, item_scheme_name, item_scheme, value, action=None):
        return self.validate.field_update(item_scheme_name, item_scheme, value, action)

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
            # Registra lista de campos default
            self.__fields = fields

    # --------------------------------
    # info
    # --------------------------------
    # TODO:: Implementar info nos documentos inseridos e atualizados
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
    # Define o limite de documentos retornados
    #
    # ?limit=20
    #
    def limit(self, max_limit=0):
        # Condigura o limite default do serviço
        limit = self.__default_limit

        # Verifica se o limit da ação foi definido
        if self.__limit > 0:
            # Recupera o limite da operação para validar
            limit = error_limit = self.__limit

            # Verifica se o limite da operação maior do que o maximo permitido pelo serviço
            if limit > self.__max_limit:

                # Caso seja, então registra o limite maximo permitido
                limit = error_max_limit = self.__max_limit

                # Verifica se um limite máximo foi definido pelo desenvolvedor do serviço
                if (max_limit > 0) and (limit > max_limit):
                    # Caso seja, então registra o limite maximo permitido
                    error_max_limit = max_limit
                    limit = max_limit

                # Registra mensagem de erro no serviço de log
                self.status.warn("MAX_LIMIT_EXCEEDED", None,
                                 [self.__data_types.to_str(error_max_limit), self.__data_types.to_str(error_limit)])

        self.__limit = limit

    # --------------------------------
    # method
    # --------------------------------
    def method(self):
        return self.__method

    # --------------------------------
    # owner_id
    # --------------------------------
    # Armazena na _info o token do dono do documento
    #
    def owner_id(self):
        self.__info["owner"] = {
            "id": self.__token
        }

    # --------------------------------
    # owner_last_id
    # --------------------------------
    # Armazena na _info o último token do usuário que alterou o documento
    #
    def owner_last_id(self):
        self.__info["owner"] = {
            "last_id": self.token
        }

    # --------------------------------
    # result_type
    # --------------------------------
    def result_type(self, result_type):
        self.__result_type = result_type

    # --------------------------------
    # send_database
    # --------------------------------
    # TODO:: Implementar melhorias na verificação de disponibilidade do serviço para serguir adiante, chegando todos os tipos que serão enviados
    # TODO:: Verificar se os dados para serem enviados ao serviço de banco de dados estão dentro das especificações esperadas
    def send_database(self):
        message = {
            "action": self.__action,
            "collection": self.__collection,
            "connection_id": self.__connection_id,
            "data": self.__data,
            "database": self.__data_base,
            "errors": self.status.to_list(),
            "fields": self.__fields,
            "filter": self.__filter.to_list(),
            "limit": self.__limit,
            "offset": self.__offset,
            "method": self.__method,
            "result_type": self.__result_type,
            "sort": self.__sort,
            "service_id": self.__data_base_id,
            "info": self.info()
        }

        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps(message)

    # --------------------------------
    # send_error
    # --------------------------------
    # Montar mensagem de erro para ser retornada ao servidor rest
    # TODO: Preparar filtro para ser retornado ao cliente
    def send_error(self):
        return dumps({
            "connection_id": self.__connection_id,
            "message": {
                "success": False,
                "message": "Falha de interação com microserviço",
                "elapsed_time": {"response": "17.000", "server": "7.000"},
                "errors": self.status.to_list(),
                "query": {
                    "limit": self.__limit,
                    "offset": self.__offset,
                    "fields": self.__fields,
                    "filter": self.__filter.to_list()
                },
            }
        })

    # --------------------------------
    # source
    # --------------------------------
    def source(self):
        return self.__source

    # --------------------------------
    # validate_service
    # --------------------------------
    # Testa a validade do serviço
    #
    def validate_service(self, service, service_id):
        if (self.__service != service) or (self.__data_types.to_str(self.__service_id)) != (self.__data_types.to_str(service_id)):
            # Registra mensagem de erro no serviço de log
            self.status.error("FALHA_DE_SERVICE", None, [self.__service, service, self.__data_types.to_str(
                self.__service_id), self.__data_types.to_str(service_id)])
            return False
        return True

    # --------------------------------
    # __filter_extras
    # --------------------------------
    # Todo Finalizar sistema de seach e regex
    def __filter_extras(self):
        # self.__prepare_regex()
        self.__prepare_search()

    # --------------------------------
    # __prepare_regex
    # --------------------------------
    def __prepare_regex(self):
        print self.__regex

    # --------------------------------
    # __prepare_search
    # --------------------------------
    # { name: { $regex: "s3", $options: "si" } }
    # or{quantity.lt(20)|price(10)}
    # tags.in( '{ $regex: "s3", $options: "si" }', '{ $regex: "s3", $options: "si" }')
    def __prepare_search(self):
        values, fields = self.__search.split(';')
        values = values.split()
        fields = fields.split(',')
        if len(fields) > 0:
            for item in fields:
                for word in values:
                    # self.__filter.add("_id.eq", result.group(2))
                    print "------->", word

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
