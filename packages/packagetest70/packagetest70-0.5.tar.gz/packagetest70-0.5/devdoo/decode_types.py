#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from devdoo.datatypes import DataTypes


class DecodeTypes:
    # --------------------------------
    # __init__
    # --------------------------------
    def __init__(self, status):
        self.status = status

    # --------------------------------
    # action
    # --------------------------------
    # Verifica se a action é do tipo string
    # caso contrário registra um erro e retorna None
    def action(self, value):
        # Verifica se o action é do tipo string
        if not DataTypes.is_string(value):
            self.status.error("SERVICE_INVALID", None, ["action", DataTypes.to_str(value)])
            return None
        return value

    # --------------------------------
    # connection_id
    # --------------------------------
    # Verifica se connection_id é um identificador válido
    # caso contrário registra um erro e retorna None
    def connection_id(self, value):
        # Verifica se o action é do tipo string
        if not re.match("^([0-9a-f]{24})$", value, re.IGNORECASE):
            self.status.error("SERVICE_INVALID", None, ["connection_id", DataTypes.to_str(value)])
        return value
