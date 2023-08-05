# -*- coding: utf-8 -*-

import locale
import html
import re

from babel.dates import format_datetime
from dateutil import parser
from num2words import num2words
from secretary import Renderer
from xml.dom.minidom import parseString


# Regex explain :
#     - starts with {{, regardless of any spaces                          ^{{\s*
#     - then, a big-ass "if"...                                           (?:
#         - with a number, with any dots or comma, (naming the group)       (?P<number>[\d,\.]+)
#     - or...                                                             |
#         - if we have a quoted string, (still naming the group)            (?P<quoted>\".*?\")
#     - or...                                                             |
#         - if we do have a variable name (still naming the group)...       (?P<variable>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - end if                                                            )
#     - then, any spaces                                                  \s*
#     - then, maybe a pipe with some method behind that we don't want     (?:\|.*)?
#     - then, the closing brackets                                        }}$
var_regexp = r"^{{\s*(?:(?P<number>[\d,\.]+)|(?P<quoted>\".*?\")|(?P<variable>\w*?)(?:\.\w*?)?)\s*(?:\|.*)?}}$"

# Regex explain :
#     - starts with "{% for ", regardless of any spaces                   ^{%\s*for\s*
#     - then, the catch variable                                          (?P<subvar>\w*?)
#         - maybe with a dot, and the following, that we don't want       (?:\.\w*?)?
#     - "in", regardless of any spaces                                    \s*in\s*
#     - then, a big-ass "if"...                                           (?:
#         - with a number, with any dots or comma, (naming the group)       (?P<number>[\d,\.]+)
#     - or...                                                             |
#         - if we have a quoted string, (still naming the group)            (?P<quoted>\".*?\")
#     - or...                                                             |
#         - if we do have a variable name (still naming the group)...       (?P<variable>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - end if                                                            )
#     - then, any spaces                                                  \s*
#     - then, the closing brackets                                        %}$
for_regexp = r"^{%\s*for\s*(?P<subvar>\w*?)(?:\.\w*?)?\s*in\s*(?:(?P<number>[\d,\.]+)|(?P<quoted>\".*?\")|(?P<variable>\w*?)(?:\.\w*?)?)\s*%}$"


class MoustacheRender(Renderer):

    def __init__(self, environment=None, **kwargs):
        Renderer.__init__(self, environment=None, **kwargs)
        self.environment.filters['date_format'] = self.date_format
        self.environment.filters['date_courte'] = self.date_courte
        self.environment.filters['date_longue'] = self.date_longue
        self.environment.filters['num_to_word'] = self.num_to_word
        self.environment.filters['format_num'] = self.format_num
        self.environment.filters['format_monnaie'] = self.format_monnaie

    @staticmethod
    def date_format(value, formatstr):
        dt = parser.parse(value)
        # format = "dd MMMM yyyy à HH:mm"
        # We have to unescape HTML char because jinja template add them automaticaly
        return format_datetime(dt, html.unescape(formatstr), locale='fr')

    def date_courte(self, value):
        return self.date_format(value, "dd/MM/yyyy")

    def date_longue(self, value):
        return self.date_format(value, "dd MMMM yyyy")

    @staticmethod
    def num_to_word(value):
        if isinstance(value, str):
            value = int(value)

        return num2words(value, lang='fr')

    @staticmethod
    def format_monnaie(value):
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

    def get_tags(self, document):
        raw_tags = self.get_raw_tags(document)
        tags = MoustacheRender.parse_tags(raw_tags)
        return tags

    def get_raw_tags(self, template):
        files = self._unpack_template(template)
        content = parseString(files['content.xml'])
        tags = MoustacheRender.list_tags(content)
        return tags

    @staticmethod
    def parse_tags(raw_tags):
        tags = []
        current_subvars = []

        for raw_tag in raw_tags:
            print("Raw_tags = " + raw_tag)

            match = re.match(var_regexp, raw_tag)
            if match and match.group("variable"):
                print("match variable : " + str(match.group("variable")))
                tags.append(match.group("variable"))
                continue

        return tags

    @staticmethod
    def list_tags(document):
        tags = document.getElementsByTagName('text:text-input')
        jinja_tags = []
        for tag in tags:
            if not tag.hasChildNodes():
                continue

            content = tag.childNodes[0].data.strip()
            jinja_tags.append(content)

        return jinja_tags
