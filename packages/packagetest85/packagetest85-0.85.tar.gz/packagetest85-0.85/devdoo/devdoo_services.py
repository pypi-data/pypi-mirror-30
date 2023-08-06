#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from service import Service


# TODO:: Implementar autoconfiguração do serviço, comunicação com console admin
class DevdooServices(object):
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        # Define parâmetros globais
        self.actions = service_config["actions"]
        self.id = service_config["id"]
        self.name = service_config["name"]
        self.schemes = service_config["schemes"]
        self.custom_service = None

        # Define endpoins de conexão
        self.broker_rest_endpoint = service_config["broker_rest_endpoint"]
        self.broker_db_endpoint = service_config["broker_database_endpoint"]
        context = zmq.Context()

        # Adaptador de conexão broker
        self.socket_broker_rest = context.socket(zmq.REP)
        self.socket_broker_rest.connect(self.broker_rest_endpoint)

        # Adaptador de conexão worker
        self.socket_broker_database = context.socket(zmq.REQ)
        self.socket_broker_database.connect(self.broker_db_endpoint)

        # Serviço a ser executado
        self.service = None

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
            # Envia mensagem para o servidor de banco de dados
            self.socket_broker_database.send(self.service.send_database())

            # Recebe mensagem do servidor de banco de dados
            msg = self.socket_broker_database.recv()

            # Envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(msg)

        # Em caso de falha
        else:
            # Nao processa a operação e envia mensagem de retorno para o cliente
            self.socket_broker_rest.send(self.service.send_error())

    # --------------------------------
    # process
    # --------------------------------
    # Inicia o Serviço
    #
    # TODO:: Mudar a forma como deverá ser configurado o serviço
    def process(self, message):
        self.service = Service(message, self.id, self.name, self.schemes, self.actions, self.custom_service)

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
            except Exception as inst:
                print "API::RUN::ERROR", inst.args[0]
