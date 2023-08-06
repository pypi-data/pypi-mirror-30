#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from core import Core
from convert import Convert
from service import Service


class DevdooServices(Core):
    # --------------------------------
    # Error
    # --------------------------------
    # TODO:: Remover classe de error
    class Error(Exception):
        pass

    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        super(DevdooServices, self).__init__()

        self.service = None
        self.config = self.init_config()

        if self.config.ready():
            self.__start()
        else:
            # TODO:: Enviar para o servidor console a informação de falha de configuração
            print Convert.to_str("AAA - FALHA NA INICIALIZACAO DO DEVDOO-BROKER-SERVICE")
            print "ERROR", self.status.to_list()

    # --------------------------------
    # __start
    # --------------------------------
    def __start(self):

        if self.__is_start_services() is True:
            # Cria contexto ZMQ
            context = zmq.Context()

            # Adaptador de conexão broker
            self.socket_broker_rest = context.socket(zmq.REP)
            self.socket_broker_rest.connect(self.config.endpoint_broker_rest)

            # Adaptador de conexão worker
            self.socket_broker_database = context.socket(zmq.REQ)
            self.socket_broker_database.connect(self.config.endpoint_broker_database)

            self.run()
        else:
            print "BBB - FALHA NA INICIALIZAÇÃO DO DEVDOO-BROKER-SERVICE"

    # --------------------------------
    # __is_start_services
    # --------------------------------
    def __is_start_services(self):

        self.config.load_devdoo_services()
        return self.config.ready()

    # --------------------------------
    # console_service_list
    # --------------------------------
    # Obtém da console a lista de configuração
    #
    # TODO:: Remover console_service_list, implementar sistema de autoconfiguração
    def console_service_list(self, server_console, service_id):
        return server_console[service_id]

    # --------------------------------
    # operation
    # --------------------------------
    # Executa a ação do Serviço
    #
    # TODO:: Implementar melhorias na verificação de disponibilidade do serviço para serguir adiante, chegando todos os tipos que serão enviados
    def operation(self):
        # Recebe do mensagem do servidor cliente
        message = self.socket_broker_rest.recv()

        # Inicia o Serviço
        self.process(message)

        # Executa a ação do Serviço
        self.service.action()

        # Verifica se o servico está pronto
        if self.service.ready():
            print "SOCKET VALIDO ENVIOU ADIANTE", "----->>>>"
            # Envia mensagem para o servidor de banco de dados
            self.socket_broker_database.send(self.service.send_database())

            # Recebe mensagem do servidor de banco de dados
            # Envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.socket_broker_database.recv())
            print "SOCKET VALIDO VOLTOU", "----->>>>"

        # Em caso de falha
        else:
            print "SERVICE FALHOU", "----->>>>", self.service.send_error(), "<<<<--------"
            # Nao processa a operação e envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.service.send_error())

    # --------------------------------
    # process
    # --------------------------------
    # Inicia o Serviço
    #
    # TODO:: Mudar a forma como deverá ser configurado o serviço
    def process(self, message):
        self.service = Service(message, self.config)

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #
    # TODO:: Implementar ping de verificação de disponibilidade do serviço
    def run(self):
        while True:
            try:
                self.operation()
            except DevdooServices.Error:
                pass

                # except Exception as inst:
                #    print "API::RUN::ERROR", inst.args
