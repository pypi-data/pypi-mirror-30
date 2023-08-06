#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datarest import DataRest
from database import DataBase
from datatypes import DataTypes
from status import Status


class Service(object):
    def __init__(self, message, service_id, name, schemes, actions, custom_service=None):
        self.actions = actions
        self.id = service_id
        self.name = name
        self.schemes = schemes
        self.status = Status()

        self.__data_types = DataTypes()
        self.__data_base = DataBase()
        self.__data_rest = DataRest(message, custom_service, self.status)
        self.__max_limit = 100

    # --------------------------------
    # action
    # --------------------------------
    def action(self):
        source = self.__data_rest.source()
        method = self.__data_rest.method()

        # Verifica se o endereço da api existe
        if source in self.actions[method].keys():
            # Recupera o objeto de configuração da api
            service_api = self.actions[method][source]
            action = service_api["action"]
            action_collection = action["collection"]
            action_db = action["database_action"]
            action_scheme = action["scheme"]
            action_type = action["result_type"]

            self.__data_rest.result_type(action_type)

            if hasattr(self, action_db) and self.__data_rest.validate_service(self.name, self.id):
                method = getattr(self, action_db)
                if action_db == "insert":
                    method(action_collection, self.__get_scheme(action_scheme, self.schemes))
                elif action_db == "remove":
                    method(action_collection)
                elif action_db == "update":
                    method(action_collection, self.__get_scheme(action_scheme, self.schemes), self.schemes)
                else:
                    method(action_collection, self.__get_scheme(self.__get_scheme(action_scheme, self.schemes), self.schemes),
                           self.get_max_limit(action))
            else:
                self.status.error("INVALID_ACTION", None, [source, self.name, self.__data_types.to_str(service_api["action"]), method])

        else:
            self.status.error("INVALID_ENDPOINT", None, [source, self.name, method])

    # --------------------------------
    # find
    # --------------------------------
    def find(self, collection, list_scheme, max_limit=None):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.__data_rest.action_db("find")

        # Recupera o identificador da coleção
        self.__data_rest.collection(collection)

        # Prepara a lista de campos válidos que poderão ser recuperados na base de dados
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        fields, dev_fields_errors = self.__data_base.fields_find(list_scheme)

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.status.error("FIELD_CONFLICT", None, [item_field_name])

        # Registra campos que devem ser retornados
        self.__data_rest.fields(fields)
        self.__data_rest.limit(max_limit)

    # --------------------------------
    # get_max_limit
    # --------------------------------
    @staticmethod
    def get_max_limit(action):
        if "max_limit" in action:
            return action["max_limit"]
        return None

    # --------------------------------
    # insert
    # --------------------------------
    # Prepara documento para ser inserido base de dados
    def insert(self, collection, list_scheme):
        list_insert_data = []

        # Define o tipo de ação que será executada no servidor de base de dados
        self.__data_rest.action_db("insert")

        # Recupera o identificador da coleção
        self.__data_rest.collection(collection)

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean, body_field_errors, dev_fields_errors = self.__data_base.fields_insert(self.__data_rest.body, list_scheme)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o esquema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser insrido na base de dados
            field_name, field_value = self.__data_rest.field_insert(item_scheme_name, item_scheme, field_value, "custom_insert")

            # Verifica se o campo não está com erro de validação
            if field_value != '__error__' and field_value != '__ERROR__':
                # Registra o campo na lista de dados que deverá ser enviada para o servidor de base de dados
                if field_name != "id":
                    list_insert_data.append({"field": field_name, "value": field_value})

        # Prepara s lista de campos que será enviada para o servidor de base de dados
        # Prepara a lista de campos que devrá ser retornada do servidor depois de salvar na base de dados
        list_insert_data = self.__prepare_insert_data_fields(list_insert_data)

        # Registra os dados do documento
        self.__data_rest.data(list_insert_data)

        # Registra as datas de criação e alteração do documento
        self.__data_rest.created_time()
        self.__data_rest.changed_time()

        # Caso o campo nao esteja registrado no scheme, registra mensagem de error
        for item_field_name in body_field_errors:
            self.status.error("DOES_NOT_EXIST_FIELD", None, [item_field_name])

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.status.error("FIELD_CONFLICT", None, [item_field_name])

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_insert_data) <= 0:
            self.status.error("NO_DATA_TO_INSERT", None, [])

    # --------------------------------
    # is_valid_scheme
    # --------------------------------
    @staticmethod
    def is_valid_scheme(scheme):
        if type(scheme) == dict:
            list_scheme = ["$currentDate", "$inc", "$min", "$max", "$mul", "$rename", "$set", "$setOnInsert", "$unset"]
            for key in scheme.keys():
                if key in list_scheme:
                    return True
        return False

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
    # TODO:: Implementar melhorias na verificação de disponibilidade do serviço para serguir adiante, chegando todos os tipos que serão enviados
    def ready(self):
        return self.status.ready()

    # --------------------------------
    # remove
    # --------------------------------
    def remove(self, collection):
        # Define o tipo de ação que será executada no servidor de base de dados
        self.__data_rest.action_db("remove")

        # Recupera o identificador da coleção
        self.__data_rest.collection(collection)

    # --------------------------------
    # send_database
    # --------------------------------
    def send_database(self):
        return self.__data_rest.send_database()

    # --------------------------------
    # send_error
    # --------------------------------
    def send_error(self):
        return self.__data_rest.send_error()

    # --------------------------------
    # update
    # --------------------------------
    def update(self, collection, scheme, list_scheme):
        # Validar configuração de schema para update, erro developer
        if self.is_valid_scheme(scheme):
            # Define o tipo de ação que será executada no servidor de base de dados
            self.__data_rest.action_db("update")

            # Recupera o identificador da coleção
            self.__data_rest.collection(collection)

            update_data = {}
            fields = ["_id"]
            for item_scheme in scheme:
                obj_item_scheme = self.__get_scheme(scheme[item_scheme], list_scheme)
                obj_item_scheme = self.update_config(obj_item_scheme)

                if len(obj_item_scheme.keys()) > 0:
                    fields = fields + obj_item_scheme.keys()
                    update_data[item_scheme] = obj_item_scheme

            # Registra os dados do documento
            self.__data_rest.data(update_data)

            # Registra campos que devem ser retornados
            self.__data_rest.fields(fields)

            # Registra as datas de criação e alteração do documento
            self.__data_rest.changed_time()

            # Verificar se tem algo para gravar no banco
            if len(update_data.keys()) <= 0:
                self.status.error("NO_DATA_TO_UPDATE", None, [])
        else:
            self.status.error("INVALID_SCHEME_UPDATE", None, [])

    # --------------------------------
    # update_config
    # --------------------------------
    # TODO:: implementar checksum de update
    def update_config(self, list_scheme):

        list_update_data = []

        # Prepara a lista de campos válidos que poderão ser inseridos na base de dados
        # Recebe a lista de erros em campos recebidos no body
        # Recebe a lista de erros em campos definido pelo desenvolvedor de microserviço
        list_scheme_clean, body_field_errors, dev_fields_errors = self.__data_base.fields_update(self.__data_rest.body, list_scheme)

        # Processa todos os campos registrados no schema para validar os valores e formatar
        for item_scheme_name in list_scheme_clean:
            # Recupera o equema para validar e formatar
            item_scheme = list_scheme_clean[item_scheme_name]

            # Recupera o valor que deverá ser validado e formatado
            field_value = item_scheme["value"]

            # Valida o campo e valor
            # Recebe o nome do campo que será inserido na base de dados e depois retornado
            # Recebe o valor que deverá ser inserido na base de dados
            field_name, field_value = self.__data_rest.field_update(item_scheme_name, item_scheme, field_value, "custom_update")

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

        # Caso o campo esteja em conflito no modo desenvolvedor de microserviço, registra mensagem de error
        for item_field_name in dev_fields_errors:
            self.status.error("FIELD_CONFLICT", None, [item_field_name])

        # Verificar se tem algo para gravar no banco, caso contrário, registra mensagem de error
        if len(list_update_data) <= 0:
            self.status.error("NO_DATA_TO_UPDATE", None, [])

        return list_update_data

    # --------------------------------
    # __get_scheme
    # --------------------------------
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
        self.__data_rest.fields(fields)

        return result
