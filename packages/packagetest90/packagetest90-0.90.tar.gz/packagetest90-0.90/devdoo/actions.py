#!/usr/bin/env python
# -*- coding: utf-8 -*-

from endpoint import Endpoint
from pprint import pprint

class Actions:
    def __init__(self, database, status):
        self.status = status
        self.__endpoints = {}
        self.__prepare_scheme(database)

    # --------------------------------
    # endpoint
    # --------------------------------
    def endpoint(self, source):
        if source in self.__endpoints.keys():
            return self.__endpoints[source]
        else:
            return None

    # --------------------------------
    # __collection
    # --------------------------------
    def __collection(self, uri, item, collections):
        collection = None
        name = None
        if "collection" in item.keys():
            name = item["collection"]
            if name in collections.keys():
                collection = collections[name]["schemes"]
            else:
                self.status.error("COLLECTION_INVALID", None, [name])
        else:
            self.status.error("COLLECTION_INVALID_IDENTIFIER", None, [uri])

        return name, collection

    # --------------------------------
    # __fields_public
    # --------------------------------
    @staticmethod
    def __fields_public(item, schemes):
        for i in schemes:
            if "public" in schemes[i].keys():
                item["scheme"][i] = schemes[i]
                if schemes[i]["public"] is True:
                    (item["fields"]["public"]).append(schemes[i]["field"])

        return item

    # --------------------------------
    # __prepare_scheme
    # --------------------------------
    def __prepare_scheme(self, database):
        collections = database["collections"]
        actions = database["actions"]
        for method in actions:
            endpoint = actions[method]
            for item in endpoint:
                name, schemes = self.__collection(item, endpoint[item], collections)
                if schemes is not None:
                    if self.__check_endpoint(item, endpoint[item]):
                        endpoint[item] = self.__fields_public(endpoint[item], schemes)
                        endpoint[item]["fields"]["default"] = self.__check_conflit_fields(endpoint[item]["fields"]["default"])
                        endpoint[item]["fields"]["public"] = self.__check_conflit_fields(endpoint[item]["fields"]["public"])
                        self.__endpoints[item] = Endpoint(item, endpoint[item], self.status)
                        if method == "put":
                            print "PUT", "----->>>"
                            pprint(endpoint[item])

    # --------------------------------
    # __check_endpoint
    # --------------------------------
    def __check_endpoint(self, uri, endpoint):
        errors = []
        if "action" not in endpoint.keys():
            errors.append("ACTION")

        if "collection" not in endpoint.keys():
            errors.append("COLLECTION")

        if "fields" not in endpoint.keys():
            errors.append("FIELDS")

        if "scheme" not in endpoint.keys():
            errors.append("SCHEME")

        if "type" not in endpoint.keys():
            errors.append("TYPE")

        if "max_limit" not in endpoint.keys():
            errors.append("MAX_LIMIT")

        if len(errors) > 0:
            self.status.error("INVALID_ENDPOINT_PARAMS", None, [(",".join(errors)), uri])
            return False
        else:
            return True

    # --------------------------------
    # __check_conflit_fields
    # --------------------------------
    # Verifica se existe conflito de nomes de campos em modo desenvolvimento de microserviços
    # Não permite incluir na lista campos pai que possuem campos filhos que podem sobrepor informações
    def __check_conflit_fields(self, fields_default):
        fields_clean = []
        fields_errors = {}

        # Processa a lista de campos default
        for item_check in fields_default:
            # Retira um item da lista para comparar com outros itens da mesma lista
            for item_field in fields_default:
                # Caso um campo esteja em conflito com outros campos é adicionado na lista de erros
                if item_check + '.' in item_field:
                    fields_errors[item_check] = True

        # Gera a lista de campos default sem os campos que foram encontrados conflitos
        for item_field in fields_default:
            if item_field not in fields_errors.keys():
                fields_clean.append(item_field)

        if len(fields_errors) > 0:
            self.status.error("FIELD_CONFLICT", None, [(",".join(fields_errors))])

        return fields_clean
