#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from datatypes import DataTypes
from console import Console
from status import Status
from zmq.sugar.socket import Socket

import yaml
import os
import sys


class DevdooBrokers(object):
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

        # Inicia os tipos de dados
        self.id = None
        self.ip = None
        self.type = None
        self.service_id = None

        self.data_types = DataTypes()
        self.console = Console()
        self.status = Status()


        print "INIT BROKER"
        '''
        self.config = self.__config()

        # Inicializa variável de conexão
        self.socket_backend = None

        if self.config is not None:
            self.id = self.config["id"]
            self.ip = self.config["ip"]
            self.type = self.config["type"]
            self.service_id = self.config["service_id"]

            # Cria contexto ZMQ
            self.context = zmq.Context()

            # Inicializa o poll set
            self.poller = zmq.Poller()

            self.__start()

        else:
            # TODO:: Enviar para o servidor console a informação de falha de configuração
            print DataTypes.to_str( "AAA - FALHA NA INICIALIZACAO DO DEVDOO-BROKER-SERVICE")
            print "ERROR", self.status.to_list()
        '''

    # --------------------------------
    # __start
    # --------------------------------
    def __start(self):
        broker_endpoint = "tcp://*:" + self.data_types.to_str(self.service_id)

        # Abre porta para o Restify (frontend)
        self.socket_frontend = self.context.socket(zmq.ROUTER)
        self.socket_frontend.bind(broker_endpoint)
        self.poller.register(self.socket_frontend, zmq.POLLIN)

        if self.__is_start_services() is True:
            self.run()
        else:
            print "BBB - FALHA NA INICIALIZAÇÃO DO DEVDOO-BROKER-SERVICE"


    # --------------------------------
    # __is_start_services
    # --------------------------------
    def __is_start_services(self):
        status = False
        list_services = self.console.services_config(self.id)

        if len(list_services) > 0:
            # Abre portas para os Serviços
            self.available_services = {}
            for item in list_services:
                # Define o endpoint do serviço
                service_id = self.data_types.to_str(item["service_id"])
                endpoint = "tcp://*:" + service_id

                print "endpoint", endpoint

                # Abre portas para os Serviços no backend
                socket_backend = self.context.socket(zmq.DEALER)
                socket_backend.bind(endpoint)

                # TODO:: Implementar Lista de serviços do mesmo tipo
                # TODO:: Aprimorar registro do serviço no stack
                # Armazena a conexão do backend no stack
                self.available_services[service_id] = socket_backend

            if len(self.available_services.keys()) > 0:
                status = True

        return status

    # --------------------------------
    # operation
    # --------------------------------
    # Permuta pacotes entre o frontend e o backend
    #
    # TODO:: Verificar se existe um serviço para o service_id solicitado antes de tentar pegar na lista
    # TODO:: Verificar se o serviço está disponível antes de tentar fazer conexão
    # TODO:: Verificar se a mensagem foi corretamente convertida de string para dic antes de tentar pegar um elemento
    # TODO:: Procurar formas de desregistrar sockets que não obtiveram respostas dentro do tempo limite
    def operation(self):
        # Poller de sockets
        socks = dict(self.poller.poll())

        # Verifica se o socket chegou do REST ou Serviço
        if socks.get(self.socket_frontend) == zmq.POLLIN:
            # Recebe mensagem do Restify
            message = self.socket_frontend.recv_multipart()

            # Recupera o socket de conexao do serviço
            self.socket_backend, service_id = self.__find_socket(message)

            # Verifica se o socket é valido
            if type(self.socket_backend) == Socket:
                print "SOCKT VALIDO", service_id
                # Registra o socket no poller ZMQ para dar acesso aos workers
                self.poller.register(self.socket_backend, zmq.POLLIN)

                # Envia ao Service Work a mensagem com pacote de dados
                self.socket_backend.send_multipart(message)
            else:
                print "FALHOU, VOLTOU PARA REST"
                # Caso contrario retorna para o cliente sem realizar nenhuma alteração
                self.socket_frontend.send_multipart(message)

        # Verifica se o socket retornou do Service Worker
        if socks.get(self.socket_backend) == zmq.POLLIN:
            # Recebe do Service Worker
            message = self.socket_backend.recv_multipart()

            # Retorna ao Restify
            self.socket_frontend.send_multipart(message)
            self.poller.unregister(self.socket_backend)

    # --------------------------------
    # process
    # --------------------------------
    # Assinatura do método process para sobrescrita
    #
    def process(self, data):
        raise DevdooBrokers.Error("`process` should be overriden")

    # --------------------------------
    # run
    # --------------------------------
    # Executa a operação em um loop infinito
    #
    def run(self):
        while True:
            try:
                self.operation()
            except Exception as inst:
                print "BROKER::RUN::ERROR", inst.args[0]

    # --------------------------------
    # __find_socket
    # --------------------------------
    def __find_socket(self, message):
        # Verifica se mensagem é string
        if (type(message) == list) and len(message) >= 3:
            # Converte mensagem para json

            # Converte a mensagem recebida do servidor rest para objeto
            package = DataTypes.to_object(message[2])

            # Verifica se o pacote de mensagem é do tipo objeto válido
            if DataTypes.is_object(package):
                # Verifica se no pacote existe o identificador do serviço
                if "service_id" in package.keys():
                    service_id = self.data_types.to_str(package["service_id"])
                    if service_id in self.available_services.keys():
                        return self.available_services[self.data_types.to_str(package["service_id"])], self.data_types.to_str(package["service_id"])

            # TODO:: Registra erro de serviço não encontrado
            return None, None

    # --------------------------------
    # __config
    # --------------------------------
    # Recupera informações de configurações do broker
    def __config(self):
        # Tenta pegar configurações docker
        devdoo_config = os.environ.get('devdoo')

        # Caso não tenha sucesso
        if not devdoo_config:
            # Tenta pegar configurações de arquivo local
            devdoo_config = self.__config_local()

        if DataTypes.is_service_config(devdoo_config):
            return devdoo_config
        else:
            self.status.error("CONFIGURATION_SERVICE", None, ["Arquivo de configuracao invalido"])
            return None

    # --------------------------------
    # __config_local
    # --------------------------------
    # Recupera informações de configuração em arquivo local
    def __config_local(self):
        config_local = None
        file_open = None

        if len(sys.argv) > 1:
            # Recupera o endereço do arquivo de configuração
            path_file = str(sys.argv[1])
            # Verifica se o endereço do arquivo é válido
            if (type(path_file) == str) and (".yml" in path_file):
                try:
                    # Abre o arquivo
                    file_yml = open(path_file, "r")
                    # Converte o arquivo em objeto
                    file_open = yaml.load(file_yml)
                except Exception as inst:
                    self.status.error("CONFIGURATION_SERVICE", None,
                                      ["Arquivo de configuracao nao encontrado"])
                    config_local = None

            # Verifica se o arquivo é válido e se existe configurações de serviços nele
            if (file_open is not None) and ("services" in file_open.keys()):
                # Processa o arquivo
                for item in file_open["services"]:
                    services = file_open["services"][item]
                    if "environment" in services:
                        environment = services["environment"]
                        if "devdoo" in environment:
                            devdoo = environment["devdoo"]
                            devdoo = DataTypes.to_object(devdoo)
                            if DataTypes.is_object(devdoo):
                                # Recupera as configurações devdoo necessárias
                                config_local = devdoo
                            else:
                                self.status.error("CONFIGURATION_SERVICE", None,
                                                  ["Arquivo de configuracao nao e um 'object' valido"])
                        self.status.error("CONFIGURATION_SERVICE", None,
                                          ["Arquivo de configuracao encontrou falhas no grupo 'devdoo'"])
                    else:
                        self.status.error("CONFIGURATION_SERVICE", None,
                                          ["Arquivo de configuracao encontrou falhas no grupo 'environment'"])
            else:
                self.status.error("CONFIGURATION_SERVICE", None,
                                  ["Arquivo de configuracao não possui o grupo 'services'"])
        else:
            self.status.error("CONFIGURATION_SERVICE", None,
                              ["Nao foi indicado nenhum endereco de arquivo de configuracao"])
        return config_local
