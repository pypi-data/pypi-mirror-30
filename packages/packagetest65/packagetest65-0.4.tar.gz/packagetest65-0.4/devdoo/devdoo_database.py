#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from service_db import ServiceDB


# TODO:: Implementar autoconfiguração do serviço, comunicação com console admin
class DevdooDatabase(object):
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        # Define endpoints de conexão
        broker_database_endpoint = service_config["broker_database_endpoint"]

        # TODO:: Melhorar forma como as configurações do banco de dados são implementadas
        self.mongodb_ip = service_config["mongodb_ip"]
        self.mongodb_port = service_config["mongodb_port"]

        # Cria o contexto ZMQ
        context = zmq.Context()

        # Adaptador de conexão
        self.socket_frontend = context.socket(zmq.REP)
        self.socket_frontend.connect(broker_database_endpoint)

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
    def operation(self):
        # Recebe do mensagem do servidor cliente
        message = self.socket_frontend.recv()
        self.process(message)

        # Processa a operacao e envia mensage de retorno para o cliente
        self.socket_frontend.send(self.service.send())

    # --------------------------------
    # process
    # --------------------------------
    # Inicia o Serviço de banco
    #
    # TODO:: Mudar a forma como deverá ser configurado o serviço
    def process(self, message):
        self.service = ServiceDB(message, self.mongodb_ip, self.mongodb_port)

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
                print "API_DB::RUN::ERROR", inst.args[0]
