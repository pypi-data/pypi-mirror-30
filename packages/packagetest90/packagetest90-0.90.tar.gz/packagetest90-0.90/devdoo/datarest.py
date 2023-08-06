#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson.json_util import dumps
from validate import Validate
from datafilter import DataFilter
from convert import Convert
from package import Package


# TODO:: Refatorar completamente a classe DataRest
# TODO:: Implementar configuração de limites definido no console para o serviço
class DataRest:
    def __init__(self, message, status):
        self.status = status
        self.package = Package(message)
        self.package.decode(status)

        if self.package.ready():
            self.__collection = None
            self.__data = {}
            self.__database_id = None
            self.__default_limit = 100
            self.__fields = []
            self.__filter = None
            self.__limit = 0
            self.__max_limit = 200
            self.__method = None
            self.__offset = 0
            self.__regex = None
            self.__result_type = None
            self.__search = None
            self.__sort = None
            self.__public_access = True

            self.validate = Validate(self.status)
            self.decode()

    # --------------------------------
    # action
    # --------------------------------
    def action(self, action):
        self.package.action = action

    # --------------------------------
    # active_service
    # --------------------------------
    def active_service(self, database_id):
        self.package.active_service(database_id)

    # --------------------------------
    # body
    # --------------------------------
    def body(self):
        return self.__body

    # --------------------------------
    # collection
    # --------------------------------
    def collection(self, collection):
        self.__collection = collection

    def data(self, data):
        self.__data = data

    # --------------------------------
    # decode_service
    # --------------------------------
    def decode(self):
        body = self.package.body
        self.__body = body["data"]
        self.__fields = body["fields"]
        self.__filter = DataFilter(body["filter"], self.status)
        self.__limit = int(body["limit"])
        self.__method = body["method"]
        self.__offset = int(body["offset"])
        self.__regex = body["regex"]
        self.__search = body["search"]
        self.__sort = body["sort"]

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
                self.status.warn("MAX_LIMIT_EXCEEDED", None, [Convert.to_str(error_max_limit), Convert.to_str(error_limit)])

        self.__limit = limit

    # --------------------------------
    # method
    # --------------------------------
    def method(self):
        return self.__method

    # --------------------------------
    # public_access
    # --------------------------------
    def public_access(self):
        return self.__public_access

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.package.ready()

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

        print "SEND DATA BASE"

        message = {
            "action": self.package.action,
            "active_port": self.package.active_port,
            "alerts": {
                "error": self.status.to_list(),
                "log": None,
                "warn": None,
                "info": None,
            },
            "app_id": self.package.app_id,
            "api_key": self.package.api_key,
            "body": {
                "collection": self.__collection,
                "data": self.__data,
                "fields": self.__fields,
                "filter": self.__filter.to_list(),
                "limit": self.__limit,
                "offset": self.__offset,
                "method": self.__method,
                "result_type": self.__result_type,
                "regex": self.__regex,
                "search": self.__search,
                "sort": self.__sort
            },
            "id": self.package.id,
            "lenght_in": self.package.lenght_in,
            "lenght_out": None,
            "service": self.package.service,
            "service_id": self.package.service_id,
            "database_id": self.package.database_id,
            "open": False,
            "source": self.package.source,
            "success": False,
            "time": {
                "time_start": None,
                "service": None,
                "database": None
            }
        }

        print "MESSAGE----->>>", message

        # Montar mensagem que será enviada para o serviço de banco de dados
        return dumps(message)

    # --------------------------------
    # send_error
    # --------------------------------
    # Montar mensagem de erro para ser retornada ao servidor rest
    # TODO: Preparar filtro para ser retornado ao cliente
    def send_error(self):
        message = {
            "action": self.package.action,
            "active_port": self.package.active_port,
            "alerts": {
                "error": self.status.to_list(),
                "log": None,
                "warn": None,
                "info": None,
            },
            "app_id": self.package.app_id,
            "api_key": self.package.api_key,
            "body": {
                "success": False,
                "message": "Falha de interação com microserviço",
                "elapsed_time": {"response": "17.000", "server": "7.000"},
                "query": {
                    "limit": self.__limit,
                    "offset": self.__offset,
                    "fields": self.__fields,
                    "filter": self.__filter.to_list()
                },
            },
            "id": self.package.id,
            "lenght_in": self.package.lenght_in,
            "lenght_out": None,
            "service": self.package.service,
            "service_id": self.package.service_id,
            "database_id": None,
            "open": False,
            "source": self.package.source,
            "success": False,
            "time": {
                "time_start": None,
                "service": None,
                "database": None
            }
        }
        return dumps(message)

    # --------------------------------
    # source
    # --------------------------------
    def source(self):
        return self.package.source

    # --------------------------------
    # validate_service
    # --------------------------------
    # Testa a validade do serviço
    #
    def validate_service(self, service, service_id):
        service = Convert.to_str(service)
        service_id = Convert.to_str(service_id)
        if (self.package.service != service) or (self.package.service_id != service_id):
            # Registra mensagem de erro no serviço de log
            self.status.error("FALHA_DE_SERVICE", None, [self.package.service, service, self.package.service_id, service_id])
            return False
        return True

    # --------------------------------
    # __filter_extras
    # --------------------------------
    # TODO:: Finalizar sistema de seach e regex
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
    # TODO:: Implementar prepare serach
    def __prepare_search(self):
        values, fields = self.__search.split(';')
        values = values.split()
        fields = fields.split(',')
        if len(fields) > 0:
            for item in fields:
                for word in values:
                    # self.__filter.add("_id.eq", result.group(2))
                    print "------->", item, word

    # --------------------------------
    # __set_source
    # --------------------------------
    # Recupera o id do documento
    '''
    def __set_source(self, source):
        # Verificar se o source possui uma id
        # Pegar a id do source
        result = re.search(r"([\s\S]+)([0-9a-f]{24})$", source)
        if result:
            source = result.group(1) + ":id"
            self.__filter.add("_id.eq", result.group(2))
        return source
    '''
