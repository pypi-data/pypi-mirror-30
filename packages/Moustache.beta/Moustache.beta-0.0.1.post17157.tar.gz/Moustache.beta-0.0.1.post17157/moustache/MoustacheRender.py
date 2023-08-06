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
#     - starts with {{, regardless of any spaces                            ^{{\s*
#     - then, a big-ass "if"...                                             (?:
#         - with a number, with any dots or comma, (naming the group)       (?P<number>[\d,\.]+)
#     - or...                                                               |
#         - if we have a quoted string, (still naming the group)            (?P<quoted>\".*?\")
#     - or...                                                               |
#         - if we do have a variable name (still naming the group)...       (?P<variable>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - end if                                                              )
#     - then, any spaces                                                    \s*
#     - then, maybe a pipe with some method behind that we don't want       (?:\|.*)?
#     - then, the closing brackets                                          }}$
var_regexp = r"^{{\s*(?:(?P<number>[\d,\.]+)|(?P<quoted>\".*?\")|(?P<variable>\w*?)(?:\.\w*?)?)\s*(?:\|.*)?}}$"

# Regex explain :
#     - starts with "{% for ", regardless of any spaces                     ^{%\s*for\s*
#     - then, the catch variable                                            (?P<subvar>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - "in", regardless of any spaces                                      \s*in\s*
#     - then, a big-ass "if"...                                             (?:
#         - with a number, with any dots or comma, (naming the group)       (?P<number>[\d,\.]+)
#     - or...                                                               |
#         - if we have a quoted string, (still naming the group)            (?P<quoted>\".*?\")
#     - or...                                                               |
#         - if we do have a variable name (still naming the group)...       (?P<variable>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - end if                                                              )
#     - then, the closing brackets                                          \s*%}$
for_regexp = r"^{%\s*for\s*(?P<subvar>\w*?)(?:\.\w*?)?\s*in\s*(?:(?P<number>[\d,\.]+)|(?P<quoted>\".*?\")|" \
             r"(?P<variable>\w*?)(?:\.\w*?)?)\s*%}$"

# Regex explain :
#     - starts with "{% if ", regardless of any spaces                      ^{%\s*if\s*
#     - then, a big-ass "if"...                                             (?:
#         - with a number, with any dots or comma, (naming the group)       (?P<number_left>[\d,\.]+)
#     - or...                                                               |
#         - if we have a quoted string, (still naming the group)            (?P<quoted_left>\".*?\")|
#     - or...                                                               |
#         - if we do have a variable name (still naming the group)...       (?P<variable_left>\w*?)
#         - maybe with a dot, and the following, that we don't want         (?:\.\w*?)?
#     - end if                                                              )
#     - then, any spaces                                                    \s*
#     - and then, maybe a comparison                                        (?:
#         - A test, with one or two =, >, <                                 [=!<>]{1,2}\s*
#         - then, a big-ass "if"...                                         (?:
#             - with a number, with any dots or comma, (naming the group)   (?P<number_right>[\d,\.]+)
#         - or...                                                           |
#             - if we have a quoted string, (still naming the group)        (?P<quoted_right>\".*?\")
#         - or...                                                           |
#             - if we do have a variable name (still naming the group)...   (?P<variable_right>\w*?)
#             - maybe with a dot, and the following, that we don't want     (?:\.\w*?)?
#         - end if                                                          )
#     - end if                                                              )?
#     - then, the closing brackets                                          \s*%}$
if_regexp = r"^{%\s*if\s*(?:(?P<number_left>[\d,\.]+)|(?P<quoted_left>\".*?\")|(?P<variable_left>\w*?)(?:\.\w*?)?)" \
            r"\s*(?:[=!<>]{1,2}\s*(?:(?P<number_right>[\d,\.]+)|(?P<quoted_right>\".*?\")|(?P<variable_right>\w*?)" \
            r"(?:\.\w*?)?))?\s*%}$"

end_for_regexp = r"{%\s*endfor\s*%}"
end_if_regexp = r"{%\s*endif\s*%}"


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
        MoustacheRender.check_statements_and_loops_integrity(raw_tags)
        tags = MoustacheRender.parse_tags(raw_tags, [])
        return tags

    def get_raw_tags(self, template):
        files = self._unpack_template(template)
        content = parseString(files['content.xml'])
        tags = MoustacheRender.list_tags(content)
        return tags

    @staticmethod
    def check_statements_and_loops_integrity(raw_tags):

        current_statement = []
        for i in range(0, len(raw_tags)):

            match = re.match(for_regexp, raw_tags[i])
            if match:
                end_index = MoustacheRender.find_closure_index(raw_tags, i)
                if not end_index:
                    raise ValueError("Error, for loop \"" + raw_tags[i] + "\" not closed")
                current_statement.append("for")
                continue

            match = re.match(if_regexp, raw_tags[0])
            if match:
                end_index = MoustacheRender.find_closure_index(raw_tags, i)
                if not end_index:
                    raise ValueError("Error, if statement \"" + raw_tags[i] + "\" not closed")
                current_statement.append("if")
                continue

            match = re.match(end_if_regexp, raw_tags[0])
            if match:
                if current_statement[len(current_statement)] == "if":
                    current_statement.pop()
                    continue
                else:
                    raise ValueError("Error, if statement closed but never opened, around statement " + str(i))

            match = re.match(end_for_regexp, raw_tags[0])
            if match:
                if current_statement[len(current_statement)] == "for":
                    current_statement.pop()
                    continue
                else:
                    raise ValueError("Error, for loop closed but never opened, around statement " + str(i))

        return True

    @staticmethod
    def parse_tags(raw_tags, current_subvars):

        tags = []
        while len(raw_tags) > 0:

            match = re.match(for_regexp, raw_tags[0])
            if match:
                current_subvars.append(match.group("subvar"))
                if match.group("variable") and match.group("variable") not in current_subvars:
                    if match.group("variable") not in tags:
                        tags.append(match.group("variable"))

                end_index = MoustacheRender.find_closure_index(raw_tags, 0)
                new_context = list(current_subvars)
                new_context.append(match.group("subvar"))
                sub_values = MoustacheRender.parse_tags(raw_tags[1:end_index], new_context)
                tags += [value for value in sub_values if value not in tags]

                del raw_tags[0:end_index + 1]
                continue

            match = re.match(if_regexp, raw_tags[0])
            if match:
                if match.group("variable_left") and match.group("variable_left") not in current_subvars:
                    if match.group("variable_left") not in tags:
                        tags.append(match.group("variable_left"))
                if match.group("variable_right") and match.group("variable_right") not in current_subvars:
                    if match.group("variable_right") not in tags:
                        tags.append(match.group("variable_right"))

                end_index = MoustacheRender.find_closure_index(raw_tags, 0)
                sub_values = MoustacheRender.parse_tags(raw_tags[1:end_index], current_subvars)
                tags += [value for value in sub_values if value not in tags]

                del raw_tags[0:end_index + 1]
                continue

            match = re.match(var_regexp, raw_tags[0])
            if match:
                if match.group("variable") and match.group("variable") not in current_subvars:
                    tags.append(match.group("variable"))

            raw_tags.pop(0)

        return tags

    @staticmethod
    def find_closure_index(raw_tags, index):
        if_count = 0
        for_count = 0

        for i in range(index + 1, len(raw_tags)):
            if re.match(for_regexp, raw_tags[i]):
                for_count += 1
            elif re.match(if_regexp, raw_tags[i]):
                if_count += 1
            elif re.match(end_for_regexp, raw_tags[i]):
                if for_count == 0:
                    return i
                else:
                    for_count -= 1
            elif re.match(end_if_regexp, raw_tags[i]):
                if if_count == 0:
                    return i
                else:
                    if_count -= 1

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
