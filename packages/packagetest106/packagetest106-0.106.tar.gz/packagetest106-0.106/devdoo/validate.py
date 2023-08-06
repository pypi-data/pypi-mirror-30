#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pydash
from devdoo.check import Check
from devdoo.convert import Convert


# TODO:: Verificar tipos inexistentes
class Validate(object):
    def __init__(self, status):
        self.status = status

    # --------------------------------
    # array
    # --------------------------------
    # Valida campo do tipo array
    # Retorna array
    #
    # Exemplos: ["a", "b", 1, 2] | a,b,c,1,2
    #
    def array(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para array
        value = Convert.to_array(value)

        # Verifica se o resultado do tipo convertido é um array válido
        if not Check.is_array(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_ARRAY", value, [field, original_value])
            value = '__error__'

        return value

    # --------------------------------
    # boolean
    # --------------------------------
    # Valida campo do tipo boleano
    # Retorna boleano
    #
    # Exemplos: TRUE, True, true, 1, FALSE, False, false, 0
    #
    def boolean(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para boleano
        value = Convert.to_boolean(value)

        # Verifica se o resultado do tipo convertido é um boleano válido
        if not Check.is_boolean(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_BOOLEAN", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # date
    # --------------------------------
    # Valida campo do tipo data
    #
    # Exemplo: 9999-12-31T23:59:59.999
    # AAAA-MM-DDTHH:MM:SS.mmm
    # AAAA-MM-DD
    # Retorna Datetime
    #
    def date(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para boleano
        value = Convert.to_date(value)

        # Verifica se o resultado do tipo convertido é uma data válida
        if not Check.is_date(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_DATE", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # decimal (float)
    # --------------------------------
    # Valida campo do tipo número decimal
    # Retorna float decimal
    #
    # TODO:: Implementar min/max para decimal
    def decimal(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para número
        value = Convert.to_decimal(value)

        # Verifica se o resultado do tipo convertido é um decimal válido
        if Check.is_decimal(value):
            pass
            # min_value / max_value
            # error_min = self.__min_value_decimal(field, value)
            # error_max = self.__max_value_decimal(field, value)
            # if error_min or error_max:
            #    value = '__error__'
        else:
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_DECIMAL", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # enum
    # --------------------------------
    # Valida campo do tipo opções de enumeração
    # Aceita somente opções string
    #
    # type: enum
    # enum:["M", "F", "34"]
    #
    def enum(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Recupera a lista de opções do enumerador
        options = Validate.type(scheme, "enum")

        # Verifica se o valor é do tipo vazio ou none
        if (value == '__empty__') or (value == '__none__') or (value not in options):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_ENUM", value, [field, Validate.clean_value(original_value), Convert.to_str(options)])
            value = '__error__'

        return value

    # --------------------------------
    # number
    # --------------------------------
    # Valida campo do tipo número longo
    #
    # type: number
    # min_value: 150
    # max_value: 300
    # formater:??
    #
    def number(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para número
        value = Convert.to_number(value)

        # Verifica se o resultado do tipo convertido é um número válido
        if Check.is_number(value):
            # min_value / max_value
            error_min = self.__min_value(scheme, value)
            error_max = self.__max_value(scheme, value)
            if error_min or error_max:
                value = '__error__'
        else:
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_NUMBER", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # object
    # --------------------------------
    # Valida campo do tipo object
    #
    # type: object
    #
    def object(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para número
        value = Convert.to_object(value)

        # Verifica se o resultado do tipo convertido é objeto válido
        if not Check.is_object(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_OBJECT", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # object_id
    # --------------------------------
    # Valida campo do tipo objectId
    #
    # type: object_id
    # Exemplo: 5abb87da835669241478b102
    def object_id(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para número
        value = Convert.to_object_id(value)

        # Verifica se o resultado do tipo convertido é um object_id válido
        if not Check.is_object_id(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_OBJECT_ID", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # string
    # --------------------------------
    #
    # Valida campo do tipo string
    #
    # type: string
    # modifier: ["uppercase", "..."]
    # min_length: 5
    # max_length: 15
    # formater:??
    #
    def string(self, scheme, value):
        value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Remove elementos indesejados da string
        value = pydash.strings.escape(value).strip()
        value = Validate.clean_value(value)

        # min_length / max_length
        error_min = self.__min_length(scheme, value)
        error_max = self.__max_length(scheme, value)
        if error_min or error_max:
            return '__error__'

        # Implementa modificadores
        return Validate.modifier(scheme, value)

    # --------------------------------
    # timestamp
    # --------------------------------
    # Valida campo do tipo timestamp
    # Exemplo: 1522239066
    def timestamp(self, scheme, value):
        # Converte valor para string
        original_value = value = Convert.to_str(value)

        # Verifica se o campo é obrigatório
        if self.__has_error_required(scheme, value):
            return '__error__'

        # Converte valor para número
        value = Convert.to_timestamp(value)

        # Verifica se o resultado do tipo convertido é um timestamp válido
        if not Check.is_timestamp(value):
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("TYPE_INVALID_TIMESTAMP", value, [field, Validate.clean_value(original_value)])
            value = '__error__'
        return value

    # --------------------------------
    # field
    # --------------------------------
    def __field(self, field_name, scheme, value, action=None):
        # Implementa valor default em caso do campo não receber valor do cliente

        field_value = Validate.default(scheme, value)
        field_type = scheme["type"]

        if hasattr(self, field_type):
            # Recupera o método do type que deverá ser executado
            method = getattr(self, field_type)
            field_value = method(scheme, field_value)
        else:
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("DOES_NOT_EXIST_FIELD_TYPE", value, [field, field_type])
            return field_name, '__error__'

        return field_name, field_value

    # --------------------------------
    # field_insert
    # --------------------------------
    def field_insert(self, item_scheme_name, scheme, value, action=None):
        field_name, field_value = self.__field(item_scheme_name, scheme, value, action)
        # Verifica se o nome do campo é dot
        if "." in field_name:
            field_name, field_value = Validate.field_dot(field_name, field_value)

        return field_name, field_value

    # --------------------------------
    # field_update
    # --------------------------------
    def field_update(self, item_scheme_name, scheme, value, action=None):
        return self.__field(item_scheme_name, scheme, value, action)

    # --------------------------------
    # default
    # --------------------------------
    @staticmethod
    def default(scheme, value):
        if (value == '__empty__') or (value is None):
            if "default" in scheme.keys():
                value = scheme["default"]
        return value

    # --------------------------------
    # clean_value
    # --------------------------------
    @staticmethod
    def clean_value(value):
        if value == '__empty__' or value == '__none__':
            value = ''
        return value

    # --------------------------------
    # check_empty
    # --------------------------------
    @staticmethod
    def check_empty(value):
        if (len(value) == 0) or (value == ''):
            value = '__empty__'
        elif value == 'null':
            value = '__none__'
        return value

    # --------------------------------
    # check_value
    # --------------------------------
    @staticmethod
    def check_value(value):
        if value == '__empty__' or value == '__none__':
            value = ''
        else:
            value = '__error__'
        return value

    # --------------------------------
    # lodash
    # --------------------------------
    # TODO:: Implementar outros modificadores
    # TODO:: Testar modificadores
    @staticmethod
    def lodash(action, value):
        if action == 'camel_case':
            value = pydash.strings.camel_case(value)
        elif action == 'clean':
            value = pydash.strings.clean(value)
        elif action == 'decapitalize':
            value = pydash.strings.decapitalize(value)
        elif action == 'escape':
            value = pydash.strings.escape(value)
        elif action == 'lowercase':
            value = pydash.strings.to_lower(value)
        elif action == 'kebab_case':
            value = pydash.strings.kebab_case(value)
        elif action == 'uppercase':
            value = pydash.strings.to_upper(value)
        elif action == 'upper_first':
            value = pydash.strings.upper_first(value)
        elif action == 'startcase':
            value = pydash.strings.start_case(value)
        elif action == 'titlecase':
            value = pydash.strings.title_case(value)
        elif action == 'unescape':
            value = pydash.strings.unescape(value)

        return value

    # --------------------------------
    # modifier
    # --------------------------------
    @staticmethod
    def modifier(field, value):
        modifier = Validate.type(field, "modifier")
        if modifier is not None:
            for action in modifier:
                value = Validate.lodash(action, value)
        return value

    # --------------------------------
    # type
    # --------------------------------
    @staticmethod
    def type(scheme, field):
        result = None
        if field in scheme.keys():
            result = scheme[field]
        return result

    # --------------------------------
    # field_dot
    # --------------------------------
    @staticmethod
    def field_dot(field_name, field_value):
        # Converte string em objetos
        def put(obj, dot_string, value):
            if "." in dot_string:
                key, rest = dot_string.split(".", 1)
                if key not in obj:
                    obj[key] = dict()
                put(obj[key], rest, value)
            else:
                obj[dot_string] = value

        d = dict()
        field_name_first, field_name = field_name.split(".", 1)
        put(d, field_name, field_value)
        return field_name_first, d

    # --------------------------------
    # __max_length
    # --------------------------------
    def __max_length(self, scheme, value):
        has_error = False
        max_length = Validate.type(scheme, "max_length")
        if (max_length is not None) and (len(value) > max_length):
            field = scheme["field"]
            has_error = True
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("MAX_LENGTH", value, [field, Convert.to_str(max_length), Convert.to_str(len(value))])
        return has_error

    # --------------------------------
    # __min_length
    # --------------------------------
    def __min_length(self, scheme, value):
        has_error = False
        min_length = Validate.type(scheme, "min_length")
        if (min_length is not None) and (len(value) < min_length):
            field = scheme["field"]
            has_error = True
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("MIN_LENGTH", value, [field, Convert.to_str(min_length), Convert.to_str(len(value))])
        return has_error

    # --------------------------------
    # __max_value
    # --------------------------------
    def __max_value(self, scheme, value):
        has_error = False
        max_value = Validate.type(scheme, "max_value")
        if value > Convert.to_number(max_value):
            field = scheme["field"]
            has_error = True
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("MAX_VALUE", value, [field, Convert.to_str(max_value), Convert.to_str(value)])
        return has_error

    # --------------------------------
    # __min_value
    # --------------------------------
    def __min_value(self, scheme, value):
        has_error = False
        min_value = Validate.type(scheme, "min_value")
        if value < Convert.to_number(min_value):
            field = scheme["field"]  # onde está a condição   valor < min_value
            has_error = True
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("MIN_VALUE", value, [field, Convert.to_str(min_value), Convert.to_str(value)])
        return has_error

    # --------------------------------
    # __has_error_required
    # --------------------------------
    def __has_error_required(self, scheme, value):
        is_required = Validate.type(scheme, "required")
        # Verifica se o campo e requerido
        if ((value == '__empty__') or (value == '')) and is_required:
            field = scheme["field"]
            # Registra mensagem de erro no serviço de log e retona ao cliente
            self.status.alerts("FIELD_REQUIRED", None, [field])
            return True
        return False
