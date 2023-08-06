#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datarest import DataRest
from check import Check


class Service(object):
    def __init__(self, message, config):
        self.config = config
        self.status = config.status
        self.endpoint = None
        self.database = config.database
        self.datarest = DataRest(message, self.status)

    # --------------------------------
    # action
    # --------------------------------
    def action(self):

        if self.datarest.ready() and self.config.ready():
            source = self.datarest.source()
            method = self.datarest.method()

            # Registra a porta do serviço de banco de dados que deve conectar
            self.datarest.active_service(self.config.active_service)
            self.endpoint = self.database.endpoint(source)
            # Verifica se o endereço da api existe
            if self.endpoint.ready():

                # Registra o tipo de retorno de dados deve executar
                self.datarest.result_type(self.endpoint.type)

                # if hasattr(self, self.endpoint.action) and self.datarest.validate_service(self.name, self.id):
                if hasattr(self, self.endpoint.action):
                    method = getattr(self, self.endpoint.action)
                    method(self.endpoint)
                else:
                    self.status.error("INVALID_ACTION", None, [source, self.config.name, self.endpoint.action, method])

            else:
                self.status.error("INVALID_ENDPOINT", None, [source, self.config.name, method])
        else:
            print "INVALID_SERVICE", "NAO ESTA PRONTO PARA EXECUTAR SERVICO", "PARAMETROS FALTANDO"
            self.status.error("INVALID_SERVICE", None, ["NAO ESTA PRONTO PARA EXECUTAR SERVICO", "PARAMETROS FALTANDO"])

    # --------------------------------
    # find
    # --------------------------------
    def find(self, endpoint):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.datarest.action("find")

        # Recupera o identificador da coleção
        self.datarest.collection(endpoint.collection)

        # Registra campos que devem ser retornados
        # TODO:: Implementar verificação de usuário logado
        self.datarest.fields(endpoint.fields(self.datarest.public_access()))
        self.datarest.limit(endpoint.max_limit)

    # --------------------------------
    # insert
    # --------------------------------
    # Prepara documento para ser inserido base de dados
    def insert(self, endpoint):
        list_insert_data = []

        # Define o tipo de ação que será executada no servidor de base de dados
        self.datarest.action("insert")

        # Recupera o identificador da coleção
        self.datarest.collection(endpoint.collection)

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean = self.database.fields_insert(self.datarest.body(), endpoint)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o esquema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser insrido na base de dados
            field_name, field_value = self.datarest.field_insert(item_scheme_name, item_scheme, field_value, "custom_insert")

            # Verifica se o campo não está com erro de validação
            if field_value != '__error__' and field_value != '__ERROR__':
                # Registra o campo na lista de dados que deverá ser enviada para o servidor de base de dados
                if field_name != "id":
                    list_insert_data.append({"field": field_name, "value": field_value})

        # Prepara s lista de campos que será enviada para o servidor de base de dados
        # Prepara a lista de campos que devrá ser retornada do servidor depois de salvar na base de dados
        list_insert_data = self.__prepare_insert_data_fields(list_insert_data)

        # Registra os dados do documento
        self.datarest.data(list_insert_data)

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_insert_data) <= 0:
            self.status.error("NO_DATA_TO_INSERT", None, [])

    # --------------------------------
    # prepare_update_data
    # --------------------------------
    # Prepara lista de campos que podem ser atualizados no documento
    @staticmethod
    def prepare_update_data(list_data):
        result = {}
        for item in list_data:
            # Registra o campo e valor na lista de campos válida do documento
            result[(item["field"])] = item["value"]
        return result

    # --------------------------------
    # ready
    # --------------------------------
    def ready(self):
        return self.datarest.ready() and self.status.ready()

    # --------------------------------
    # remove
    # --------------------------------
    def remove(self, endpoint):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.datarest.action("remove")

        # Recupera o identificador da coleção
        self.datarest.collection(endpoint.collection)

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        return self.datarest.send_database()

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        return self.datarest.send_error()

    # --------------------------------
    # update
    # --------------------------------
    def update(self, collection, scheme, list_scheme):
        # Validar configuração de schema para update, erro developer
        if Check.is_scheme(scheme):
            # Define o tipo de ação que será executada no servidor de base de dados
            self.datarest.action("update")

            # Recupera o identificador da coleção
            self.datarest.collection(collection)

            update_data = {}
            fields = ["_id"]
            for item_scheme in scheme:
                # TODO:: Remover __get_scheme do update
                obj_item_scheme = self.__get_scheme(scheme[item_scheme], list_scheme)
                obj_item_scheme = self.update_config(obj_item_scheme)

                if len(obj_item_scheme.keys()) > 0:
                    fields = fields + obj_item_scheme.keys()
                    update_data[item_scheme] = obj_item_scheme

            # Registra os dados do documento
            self.datarest.data(update_data)

            # Registra campos que devem ser retornados
            self.datarest.fields(fields)

            # Verificar se tem algo para gravar no banco
            if len(update_data.keys()) <= 0:
                self.status.error("NO_DATA_TO_UPDATE", None, [])
        else:
            self.status.error("INVALID_SCHEME_UPDATE", None, [])

    # --------------------------------
    # update_config
    # --------------------------------
    def update_config(self, list_scheme):

        list_update_data = []

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean, body_field_errors = self.database.fields_update(self.datarest.body(), list_scheme)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o equema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser inserido na base de dados
            field_name, field_value = self.datarest.field_update(item_scheme_name, item_scheme, field_value, "custom_update")

            # Verifica se o campo não está com erro de validação
            if field_value != '__error__' and field_value != '__ERROR__':
                # Registra o campo na lista de dados que deverá ser enviada para o servidor de base de dados
                if field_name != "id":
                    list_update_data.append({"field": field_name, "value": field_value})

        # Prepara a lista de campos que será enviada para o servidor de base de dados
        # Prepara a lista de campos que devrá ser retornada do servidor depois de salvar na base de dados
        list_update_data = self.prepare_update_data(list_update_data)

        # Caso o campo nao esteja registrado no scheme, registra mensagem de error
        for item_field_name in body_field_errors:
            self.status.error("DOES_NOT_EXIST_FIELD", None, [item_field_name])

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_update_data) <= 0:
            self.status.error("NO_DATA_TO_UPDATE", None, [])

        return list_update_data

    # --------------------------------
    # __get_scheme
    # --------------------------------
    # TODO: Remover __get_scheme da classe
    def __get_scheme(self, scheme, list_schemes):
        result = {}
        for field_name in scheme:
            if field_name in list_schemes.keys():
                result[field_name] = list_schemes[field_name]
            else:
                self.status.error("DOES_NOT_EXIST_FIELD", None, [field_name])
        return result

    # --------------------------------
    # __insert_data_join
    # --------------------------------
    # Função recursiva utilizada para tratar conflito de elementos filho no momento de gravar na base de dados
    #
    # data - Objeto contento dados existentes do mesmo grupo ou um objeto vazio para receber novos elementos
    # value - Dados que deverão ser inseridos no objeto
    def __insert_data_join(self, data, value):

        # Pega cada elemento do objeto valor
        for item in value:
            # Verifica se valor é um objeto
            # Verifica se o elemento filho valor é um objeto
            # Verifica se o elemento filho existe no objeto de dados
            if type(value) == dict and type(value[item]) == dict and type(data) == dict and item in data.keys():
                # Adiciona novo elemento no objeto de dados com o resultado da interação nos objetos filhos do objeto valor
                data[item] = self.__insert_data_join(data[item], value[item])

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

    # --------------------------------
    # __prepare_insert_data_fields
    # --------------------------------
    # Prepara lista de campos que podem ser incluidos no documento
    # Prepara e registra a lista de campos que deverá ser retornada do servidor após a inclusão do documento na base de dados
    def __prepare_insert_data_fields(self, list_data):
        result = {}
        fields = {}

        for item in list_data:
            # Verifica se o nome do campo existe na lista que será incluida no documento
            if (item["field"]) in result.keys():
                # Caso não esteja na lista então o campo é incluido
                # Prepara objetos filhos no padrão permitido paraga registrar na base de dados
                result[(item["field"])] = self.__insert_data_join(result[(item["field"])], item["value"])
            else:
                # Registra o campo e valor na lista de campos válida do documento
                result[(item["field"])] = item["value"]

            # Adiciona o campo na lista de campos que devem ser retornados do servidor
            fields[(item["field"])] = True

        # Registra campos que devem ser retornados
        self.datarest.fields(fields)

        return result
