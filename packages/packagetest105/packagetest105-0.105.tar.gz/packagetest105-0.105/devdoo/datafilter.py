#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ast
import bson
from check import Check
from convert import Convert


# TODO:: Refator completamente classe DataFilter
class DataFilter:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, params, status):
        list_params = self.__to_list(params)
        self.status = status
        self.labels = {"item": dict(), "list": dict()}

        self.__params = dict()
        self.__prepare(self.__params, list_params, "item")
        self.__conflict()

    # --------------------------------
    # __str__
    # --------------------------------
    def __str__(self):
        return Convert.to_str(self.__params)

    # --------------------------------
    # add
    # --------------------------------
    def add(self, field, value):
        if type(value) == str:
            prepare_filter = Convert.to_str(field + "(" + value + ")")
        else:
            prepare_filter = unicode(field + "(" + value + ")")

        self.__prepare(self.__params, [prepare_filter], 'item')

    # --------------------------------
    # check_options_values
    # --------------------------------
    # TODO:: Analisar melhor o nome desse método e onde deve ficar
    @staticmethod
    def check_options_values(key, value):
        options = ["in", "nin", "and", "or", "nor"]
        if key in options:
            if type(value) != list:
                value = [value]

                index = 0
        for item in value:
            # { name: { $regex: "s3", $options: "si" } }
            # Verifica se é do tipo regex
            if type(item) == str or type(item) == unicode and re.match(r"/([\s\S]+)/([\s\S]+)\Z", item, re.IGNORECASE):
                regex = re.match(r"/([\s\S]+)/([\s\S]+)\Z", item, re.IGNORECASE)
                value[index] = {
                    "$regex": regex.group(1),
                    "$options": regex.group(2)
                }
                index = index + 1

        return value

    # --------------------------------
    # to_list
    # --------------------------------
    def to_list(self):
        return self.__params

    # --------------------------------
    # __conflict
    # --------------------------------
    def __conflict(self):
        fields_errors = []

        # Processa a lista de campos default
        for item_check in self.labels["item"]:
            # Retira um item da lista para comparar com outros itens da mesma lista
            for item_field in self.labels["item"]:
                # Caso um campo esteja em conflito com outros campos é adicionado na lista de erros
                if item_check + '.' in item_field:
                    fields_errors.append([item_check, item_field])
        if len(fields_errors) > 0:
            self.status.warn(3363569, "ERROR:: CAMPOS EM CONFLITOS" + Convert.to_str(fields_errors))

    # --------------------------------
    # __dot_to_dict
    # --------------------------------
    def __dot_to_dict(self, d, dot_string, value):
        if dot_string == "id":
            dot_string = "_id"
        options = ["eq", "gt", "gte", "lt", "lte", "ne", "exists", "not", "type", "and", "or", "nor", "in", "nin"]
        if "." in dot_string:
            key, rest = dot_string.split(".", 1)
            if key == "id":
                key = "_id"
            if key not in d:
                key = key if key not in options else '$' + key
                d[key] = dict()
            self.__dot_to_dict(d[key], rest, value)
        elif dot_string in options:
            if type(d) == dict:
                key = '$' + dot_string
                d[key] = self.check_options_values(dot_string, value)
        else:
            d[dot_string] = value

    # --------------------------------
    # __prepare
    # --------------------------------
    def __prepare(self, group_params, list_params, type_params):
        for param in list_params:
            regex_comparison_query_perators = r"(?:([\s\S]*|\.(eq|gt|gte|lt|lte|ne|exists|not|in|nin|type))\(([\s\S]+)\))\Z"
            match_comparison_query_perators = re.match(regex_comparison_query_perators, param, re.IGNORECASE)

            regex_comparison_query_perators_and_nor = r"(?:(and|nor)\[([\s\S]*)\])\Z"
            match_comparison_query_perators_and_nor = re.match(regex_comparison_query_perators_and_nor, param, re.IGNORECASE)

            regex_comparison_query_perators_or = r"(or)\{([\s\S]*)\}\Z"
            match_comparison_query_perators_or = re.match(regex_comparison_query_perators_or, param, re.IGNORECASE)

            if match_comparison_query_perators:
                group_filter = match_comparison_query_perators.group(1)
                group_value = match_comparison_query_perators.group(3)

                if re.match(r"^([a-z0-9_]+\.?)+$", group_filter, re.IGNORECASE):
                    self.labels[type_params][group_filter] = True
                    self.__dot_to_dict(group_params, group_filter, self.__values(group_value))
                else:
                    self.status.warn(87541545, "ERROR - Filtro inválido" + Convert.to_str(group_filter))

            elif match_comparison_query_perators_and_nor:
                group_filter = match_comparison_query_perators_and_nor.group(1)
                group_value = match_comparison_query_perators_and_nor.group(2)

                if not re.match(r"(?:[a-z0-9]+\([\s\S]+\)[^+])\Z", group_value, re.IGNORECASE):
                    if re.match(r"^([a-z0-9_]+\.?)+$", group_filter, re.IGNORECASE):
                        group = group_params["$" + group_filter] = []
                        self.__values_list(group, group_value, "+")
                    else:
                        self.status.warn(523152, "ERROR FILTRO- de separador '|' nao encontrado" + Convert.to_str(group_filter))

                else:
                    self.status.warn(523152, "ERROR FILTRO- de separador '|' nao encontrado" + Convert.to_str(group_filter))

            elif regex_comparison_query_perators_or:
                group_filter = match_comparison_query_perators_or.group(1)
                group_value = match_comparison_query_perators_or.group(2)

                if not re.match(r"(?:[a-z0-9]+\([\s\S]+\)[^|])\Z", group_value, re.IGNORECASE):
                    if re.match(r"^([a-z0-9_]+\.?)+$", group_filter, re.IGNORECASE):
                        group = group_params["$" + group_filter] = []
                        self.__values_list(group, group_value, "|")
                    else:
                        self.status.warn(5454545454, "Filtro inválido" + Convert.to_str(group_filter))

                else:
                    self.status.warn(523152, "ERROR FILTRO- de separador '|' nao encontrado" + Convert.to_str(group_filter))

            else:
                self.status.warn(5454545454, "Filtro inválido XXXXXXX")

    # --------------------------------
    # __to_list
    # --------------------------------
    def __to_list(self, params, sep=";"):
        list_params = []
        if type(params) == str or type(params) == unicode:
            params = params.split(sep)
            for item in params:
                if Check.is_empty(item) is not False:
                    list_params.append(item)
        return list_params

    # --------------------------------
    # __values
    # --------------------------------
    def __values(self, value):

        # Verifica se o valor é do tipo número
        if value.isdigit() or value.replace('.', '', 1).isdigit():
            value = ast.literal_eval(value)

        # Verifica se o valor é do tipo array
        elif "," in value:
            value = value.split(",")
            i = 0
            for item in value:
                if item.isdigit() or item.replace('.', '', 1).isdigit():
                    value[i] = ast.literal_eval(item)
                    i += 1
        # Verifica se é do tipo bolean
        elif value.lower() in ["true", "1"]:
            value = True
        elif value.lower() in ["false", "0"]:
            value = False

        # Verifica se é do tipo objectID
        elif re.match("^[0-9a-f]{24}$", value):
            try:
                value = bson.objectid.ObjectId(Convert.to_str(value))
            except Exception as inst:
                value = {"error": inst.args}

        # Verifica se é do tipo date
        # Verifica se é do tipo timestamp
        # Verifica se é uma lista

        if type(value) == list:
            index = 0
            # Processa s lista para verificar se os elementos são do tipo ObjectId
            for item in value:
                # Verifica se é do tipo objectId
                if re.match("^[0-9a-f]{24}$", item):
                    try:
                        # Converte string em ObjectId
                        value[index] = bson.objectid.ObjectId(Convert.to_str(item))
                        index = index + 1
                    except Exception as inst:
                        value = {"error": inst.args}

        return value

    # --------------------------------
    # __values_list
    # --------------------------------
    def __values_list(self, group_params, values, sep):
        list_params = self.__to_list(values, sep)
        if len(list_params) > 0:
            for item in list_params:
                item_filter = dict()
                if re.match(r"(?:([\s\S]*|\.(eq|gt|gte|lt|lte|ne|exists|not|in|nin|type))\(([\s\S]+)\))\Z", item, re.IGNORECASE):
                    self.__prepare(item_filter, [item], "list")
                elif re.match(r"(or){([\s\S]*)}\Z", item, re.IGNORECASE):
                    list_items = item.split(sep)
                    self.__prepare(item_filter, list_items, "list")

                if len(item_filter.keys()) > 0:
                    group_params.append(item_filter)
