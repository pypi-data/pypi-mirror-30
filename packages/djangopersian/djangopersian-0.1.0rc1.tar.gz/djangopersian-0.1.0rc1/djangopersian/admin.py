import datetime

import pytz
from django.db import models
from django.contrib.admin import FieldListFilter
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from jdatetime import JalaliToGregorian, GregorianToJalali


class PersianDateListFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__persian' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        super(PersianDateListFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def queryset(self, request, queryset):
        v = self.lookup_val
        ir_dst = pytz.timezone('Asia/Tehran')
        nw = now().astimezone(ir_dst)
        nw_shamsi = GregorianToJalali(nw.year, nw.month, nw.day)
        date_from = None
        date_to = None
        if v == 'day':
            date_from = nw.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = date_from + datetime.timedelta(days=1)
        elif v == 'week':
            date_from = nw.replace(hour=0, minute=0, second=0, microsecond=0)
            while date_from.weekday() != 5:
                date_from -= datetime.timedelta(days=1)
            date_to = date_from + datetime.timedelta(days=7)
        elif v == 'month':
            y, m = nw_shamsi.jyear, nw_shamsi.jmonth
            month0 = JalaliToGregorian(y, m, 1).getGregorianList()
            month1 = JalaliToGregorian(y + (m + 1) // 12, 1 + (m % 12), 1).getGregorianList()
            date_from = ir_dst.localize(datetime.datetime(*month0))
            date_to = ir_dst.localize(datetime.datetime(*month1))
        elif v == 'month1':
            y, m = nw_shamsi.jyear, nw_shamsi.jmonth
            month0 = JalaliToGregorian(y, m, 1).getGregorianList()
            month1 = JalaliToGregorian(y - (1 if m == 1 else 0), (m - 1) or 12, 1).getGregorianList()
            date_from = ir_dst.localize(datetime.datetime(*month1))
            date_to = ir_dst.localize(datetime.datetime(*month0))
        if date_from:
            queryset = queryset.filter(**{self.field_path + '__gte': date_from})
        if date_to:
            queryset = queryset.filter(**{self.field_path + '__lt': date_to})
        return queryset

    def get_links(self):
        return (
            ('day', 'امروز'),
            ('week', 'این هفته'),
            ('month', 'این ماه'),
            ('month1', 'ماه گذشته'),
        )

    def choices(self, changelist):
        yield {
            'selected': not self.lookup_val or self.lookup_val == 'all',
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg]),
            'display': _('Any date'),
        }
        for lookup, title in self.get_links():
            yield {
                'selected': self.lookup_val == lookup,
                'query_string': changelist.get_query_string({
                    self.lookup_kwarg: lookup,
                }),
                'display': title,
            }

    @classmethod
    def set_as_default_filter(cls):
        FieldListFilter.register(lambda f: isinstance(f, models.DateField), cls, take_priority=True)
