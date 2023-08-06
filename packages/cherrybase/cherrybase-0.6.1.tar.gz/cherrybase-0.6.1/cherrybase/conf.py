# -*- coding: utf-8 -*-

import cherrypy
from cherrybase.utils import AttributeDict


class ConfigNamespace(object):
    '''
    Класс-утилита для чтения конфигурации
    '''

    __exit__ = None

    def __init__(self, name, defaults=None):
        '''
        Конструктор. Привязывает пространство имен к конфигурации CherryPy по умолчанию.

        :param name: Название пространства имен
        :param defaults: Значения параметров конфигурации по умолчанию
        '''
        self.config = defaults or {}
        cherrypy.config.namespaces[name] = self

    def __call__(self, key, value):
        self.config[key] = value

    def __getattr__(self, name):
        return self.config[name]

    def __getitem__(self, name):
        return self.config[name]


class DictConfigNamespace(dict):
    '''
    Класс-утилита для чтения конфигурационных словарей
    '''

    __exit__ = None

    def __init__(self, name, prefixes=(), defaults=None, default_singles=None):
        super(DictConfigNamespace, self).__init__({prefix: AttributeDict(defaults) for prefix in prefixes})
        self.defaults = defaults or {}
        self.singles = default_singles or {}
        cherrypy.config.namespaces[name] = self

    def __call__(self, key, value):
        if '.' not in key:
            self.singles[key] = value
            return

        section, key = key.split('.', 2)
        if section not in self:
            self[section] = AttributeDict(self.defaults)
        self[section][key] = value

    def __getattr__(self, name):
        return self[name]
