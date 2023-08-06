import datetime

from django.forms import Widget
from django.utils.encoding import force_text
from jdatetime import JalaliToGregorian

from .utils import to_english_str


class PersianDatePicker(Widget):
    input_type = 'text'
    template_name = 'djangopersian/persiandatepicker.html'

    class Media:
        css = {
            'all': [
                'https://cdn.jsdelivr.net/npm/persian-datepicker@1/dist/css/persian-datepicker.min.css',
            ]
        }
        js = (
            'https://cdn.jsdelivr.net/npm/persian-date@1/dist/persian-date.min.js',
            'https://cdn.jsdelivr.net/npm/persian-datepicker@1/dist/js/persian-datepicker.min.js',
        )

    def value_from_datadict(self, data, files, name):
        v = data.get(name)
        if not v:
            return None
        v = to_english_str(v).split('-')
        if len(v) != 3:
            return None
        dt = JalaliToGregorian(int(v[0]), int(v[1]), int(v[2]))
        return datetime.date(dt.gyear, dt.gmonth, dt.gday)

    def format_value(self, value):
        if value == '' or value is None:
            return None
        return force_text(value)
