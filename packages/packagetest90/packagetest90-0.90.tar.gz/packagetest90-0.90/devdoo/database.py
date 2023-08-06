#!/usr/bin/env python
# -*- coding: utf-8 -*-

from actions import Actions
from convert import Convert
from check import Check


# TODO:: Refatorar completamente a classe DataBase
class DataBase:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, database, status):
        self.status = status

        self.id = database["id"]
        self.network = database["network"]
        self.collections = database["collections"]
        self.actions = Actions(database, self.status)

    # --------------------------------
    # active_service
    # --------------------------------
    def active_service(self):
        return self.network["port"]

    # --------------------------------
    # endpoint
    # --------------------------------
    def endpoint(self, source):
        return self.actions.endpoint(source)

    # --------------------------------
    # fields_insert
    # --------------------------------
    # Prepara a lista de campos que pode ser incluída na base de dados
    #
    def fields_insert(self, body, endpoint):
        list_scheme_clean = {}

        # Verifica se o campo tem valor default
        for item_name in endpoint.scheme:
            # Pega um esquema da lista
            item_scheme = endpoint.scheme[item_name]
            # Verifica se o campo tem valor default ou é requerido
            if Check.is_default(item_scheme) or self.__required(item_scheme):
                # Registra o dot field name do campo
                item_scheme["field"] = item_name
                # Verifica se o valor do campo não é vazio
                # Registra o valor do campo
                item_scheme["value"] = Convert.to_empty(item_scheme, self.__default(item_scheme))
                # Registra o schema válido na lista de esquema limpa
                list_scheme_clean[item_name] = item_scheme

        # Processa todos os campos de body para colocar em letra minuscula e criar lista de campos validos
        for item_body_field in body:
            # Processa o nome do campo recebido no body
            body_field = item_body_field.replace(' ', '_').lower().strip()

            # Verifica se o campo recebido via body esta configurado no esquema
            item_name, item_scheme = self.__check_body_item_scheme(body_field, endpoint.scheme)

            # Caso o campo recebido via body está registrado no esquema então adiciona na lista de esquema limpa
            if item_scheme is not None:
                # Registra o dot field name do campo
                item_scheme["field"] = item_name
                # Verifica se o valor do campo não é vazio
                # Registra o valor do campo
                item_scheme["value"] = Convert.to_empty(item_scheme, body[item_body_field])
                # Registra o schema válido na lista de esquema limpa
                list_scheme_clean[item_name] = item_scheme

            # Caso o campo nao esteja registrado no scheme, registra na lista de campos com erro
            if item_body_field not in endpoint.fields(False):
                # Caso o campo nao esteja registrado no scheme, registra mensagem de error
                self.status.error("DOES_NOT_EXIST_FIELD", None, [item_body_field])

        return list_scheme_clean

    # --------------------------------
    # fields_update
    # --------------------------------
    def fields_update(self, body, list_scheme):
        fields_default = self.__fields_default(list_scheme)

        list_scheme_clean = {}
        body_field_errors = []

        # Processa todos os campos de body para colocar em letra minuscula e criar lista de campos validos
        for item_body_field in body:
            body_field = item_body_field.replace(' ', '_').lower().strip()
            item_name, item_scheme = self.__check_body_item_scheme(body_field, list_scheme)

            if item_scheme is not None:
                item_scheme["field"] = item_name
                item_scheme["value"] = Convert.to_empty(item_scheme, body[item_body_field])
                list_scheme_clean[item_name] = item_scheme

            # Caso o campo nao esteja registrado no scheme, registra mensagem de error
            if item_body_field not in fields_default:
                body_field_errors.append(item_body_field)

        return list_scheme_clean, body_field_errors

    # --------------------------------
    # __check_body_item_scheme
    # --------------------------------
    # Verifica se o campo recebido via body esta configurado no esquema
    @staticmethod
    def __check_body_item_scheme(body_field, list_scheme):
        for item_scheme in list_scheme:
            if item_scheme == body_field:
                return item_scheme, list_scheme[item_scheme]
        return None, None

    # --------------------------------
    # __default
    # --------------------------------
    @staticmethod
    def __default(item_scheme):
        value = ""
        if 'default' in item_scheme.keys():
            value = item_scheme['default']
        return value

    # --------------------------------
    # __required
    # --------------------------------
    @staticmethod
    def __required(item_scheme):
        value = False
        if 'required' in item_scheme.keys():
            value = item_scheme['required']
        return value
