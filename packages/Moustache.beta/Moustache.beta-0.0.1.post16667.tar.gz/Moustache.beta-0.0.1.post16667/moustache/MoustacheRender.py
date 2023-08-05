
#pip install babel
#pip install num2words
#pip install python-dateutil

from babel.dates import format_date, format_datetime, format_time
from secretary import Renderer
from num2words import num2words
from dateutil import parser
import locale

class MoustacheRender(Renderer):
    def __init__(self, environment=None, **kwargs):
        Renderer.__init__(self, environment=None, **kwargs)
        self.environment.filters['date_format'] = self.date_format
        self.environment.filters['date_courte'] = self.date_courte
        self.environment.filters['date_longue'] = self.date_longue
        self.environment.filters['num_to_word'] = self.num_to_word
        self.environment.filters['format_num'] = self.format_num
        self.environment.filters['monnaie'] = self.format_currency



    def date_format(self, value, format):
        dt = parser.parse(value)
        #format = "dd MMMM yyyy à HH:mm"
        return format_datetime(dt, format, locale='fr')


    def date_courte(self, value):
        return self.date_format(value, "dd/mm/yyyy")

    def date_longue(self, value):
        return self.date_format(value, "dd MMMM yyyy")


    def num_to_word(self, value):
        if isinstance(value, str):
            value = int(value)

        return num2words(value, lang='fr')


    def format_currency(self, value):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        if isinstance(value, str):
            value = int(value)

        return locale.currency(value)

    def format_num(self,value):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        if isinstance(value, str):
            value = int(value)

        return "{:n}".format(value)
