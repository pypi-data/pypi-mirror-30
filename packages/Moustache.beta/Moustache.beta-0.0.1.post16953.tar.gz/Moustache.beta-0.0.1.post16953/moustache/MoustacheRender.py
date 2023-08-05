# -*- coding: utf-8 -*-

import locale

from babel.dates import format_datetime
from dateutil import parser
from num2words import num2words
from secretary import Renderer


class MoustacheRender(Renderer):
    def __init__(self, environment=None, **kwargs):
        Renderer.__init__(self, environment=None, **kwargs)
        self.environment.filters['date_format'] = self.date_format
        self.environment.filters['date_courte'] = self.date_courte
        self.environment.filters['date_longue'] = self.date_longue
        self.environment.filters['num_to_word'] = self.num_to_word
        self.environment.filters['format_num'] = self.format_num
        self.environment.filters['monnaie'] = self.format_currency

    @staticmethod
    def date_format(value, format):
        dt = parser.parse(value)
        # format = "dd MMMM yyyy à HH:mm"
        return format_datetime(dt, format, locale='fr')

    def date_courte(self, value):
        return self.date_format(value, "dd/mm/yyyy")

    def date_longue(self, value):
        return self.date_format(value, "dd MMMM yyyy")

    @staticmethod
    def num_to_word(value):
        if isinstance(value, str):
            value = int(value)

        return num2words(value, lang='fr')

    @staticmethod
    def format_currency(value):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        if isinstance(value, str):
            value = int(value)

        return locale.currency(value)

    @staticmethod
    def format_num(value):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        if isinstance(value, str):
            value = int(value)

        return "{:n}".format(value)
