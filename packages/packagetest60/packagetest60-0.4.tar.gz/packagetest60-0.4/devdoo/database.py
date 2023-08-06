#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datatypes import DataTypes


# TODO:: Refatorar completamente a classe DataBase
class DataBase:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self):
        self.__data_types = DataTypes()

    # --------------------------------
    # fields_find
    # --------------------------------
    # Prepara a lista de campos que pode ser incluída na base de dados
    #
    def fields_find(self, list_scheme):
        return self.__fields_default(list_scheme)

    # --------------------------------
    # fields_insert
    # --------------------------------
    # Prepara a lista de campos que pode ser incluída na base de dados
    #
    def fields_insert(self, body, list_scheme):
        list_scheme_clean = {}
        body_field_errors = []

        # Recupera a lista de campos que pode ser adicionada na base de dados
        # Recupera a lista de campos que foram encontrados conflitos em modo desenvolvimento de microserviços
        fields_default, dev_fields_errors = self.__fields_default(list_scheme)

        # Verifica se o campo tem valor default
        for item_name in list_scheme:
            # Pega um esquema da lista
            item_scheme = list_scheme[item_name]
            # Verifica se o campo tem valor default ou é requerido
            if self.__has_default(item_scheme) or self.__required(item_scheme):
                # Registra o dot field name do campo
                item_scheme["field"] = item_name
                # Verifica se o valor do campo não é vazio
                # Registra o valor do campo
                item_scheme["value"] = self.__check_empty(item_scheme, self.__default(item_scheme))
                # Registra o schema válido na lista de esquema limpa
                list_scheme_clean[item_name] = item_scheme

        # Processa todos os campos de body para colocar em letra minuscula e criar lista de campos validos
        for item_body_field in body:
            # Processa o nome do campo recebido no body
            body_field = item_body_field.replace(' ', '_').lower().strip()

            # Verifica se o campo recebido via body esta configurado no esquema
            item_name, item_scheme = self.__check_body_item_scheme(body_field, list_scheme)

            # Caso o campo recebido via body está registrado no esquema então adiciona na lista de esquema limpa
            if item_scheme is not None:
                # Registra o dot field name do campo
                item_scheme["field"] = item_name
                # Verifica se o valor do campo não é vazio
                # Registra o valor do campo
                item_scheme["value"] = self.__check_empty(item_scheme, body[item_body_field])
                # Registra o schema válido na lista de esquema limpa
                list_scheme_clean[item_name] = item_scheme

            # Caso o campo nao esteja registrado no scheme, registra na lista de campos com erro
            if item_body_field not in fields_default:
                body_field_errors.append(item_body_field)

        return list_scheme_clean, body_field_errors, dev_fields_errors

    # --------------------------------
    # fields_update
    # --------------------------------
    def fields_update(self, body, list_scheme):
        fields_default, dev_fields_errors = self.__fields_default(list_scheme)

        list_scheme_clean = {}
        body_field_errors = []

        # Processa todos os campos de body para colocar em letra minuscula e criar lista de campos validos
        for item_body_field in body:
            body_field = item_body_field.replace(' ', '_').lower().strip()
            item_name, item_scheme = self.__check_body_item_scheme(body_field, list_scheme)

            if item_scheme is not None:
                item_scheme["field"] = item_name
                item_scheme["value"] = self.__check_empty(item_scheme, body[item_body_field])
                list_scheme_clean[item_name] = item_scheme

            # Caso o campo nao esteja registrado no scheme, registra mensagem de error
            if item_body_field not in fields_default:
                body_field_errors.append(item_body_field)

        return list_scheme_clean, body_field_errors, dev_fields_errors

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
    # __check_dev_fields_default
    # --------------------------------
    # Verifica se existe conflito de nomes de campos em modo desenvolvimento de microserviços
    # Não permite incluir na lista campos pai que possuem campos filhos que podem sobrepor informações
    @staticmethod
    def __check_dev_fields_default(fields_default):
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

        return fields_clean, fields_errors.keys()

    # --------------------------------
    # __check_empty
    # --------------------------------
    # Verifica se o valor do campo não está vazio ou é do tipo js null
    def __check_empty(self, item_scheme, value):
        # Verifica se o campo é diferente de string e se não está vazio
        if item_scheme["type"] != 'string' and (len(self.__data_types.to_str(value)) == 0 or value == ''):
            value = '__empty__'

        # Verifica se o valor do campo e do tipo null
        elif value == '__none__' or value == '__NONE__':
            value = None

        return value

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
    # fields_default
    # --------------------------------
    # Cria lista de campos default a partir da lista de schemas
    def __fields_default(self, list_scheme):
        # Adiciona o campo id como campo default para todas asinterações com a base de dados
        fields_default = ["_id", "id"]

        # Cria lista de campos default da api
        for item_scheme in list_scheme:
            fields_default.append(item_scheme)

        return self.__check_dev_fields_default(fields_default)

    # --------------------------------
    # __has_default
    # --------------------------------
    @staticmethod
    def __has_default(item_scheme):
        has_default = False
        if 'default' in item_scheme.keys():
            has_default = True
        return has_default

    # --------------------------------
    # __required
    # --------------------------------
    @staticmethod
    def __required(item_scheme):
        value = False
        if 'required' in item_scheme.keys():
            value = item_scheme['required']
        return value
