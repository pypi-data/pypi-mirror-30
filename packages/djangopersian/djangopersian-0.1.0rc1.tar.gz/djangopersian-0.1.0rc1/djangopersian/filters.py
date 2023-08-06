import datetime

from django.utils import formats
from jdatetime import GregorianToJalali

from .utils import ir_now, PERSIAN_MONTHS, irtz


original_date_format = formats.date_format


def persian_date_format(value, format=None, use_l10n=None):
    """
    Formats a datetime.date or datetime.datetime object using a
    localizable format

    If use_l10n is provided and is not None, that will force the value to
    be localized (or not), overriding the value of settings.USE_L10N.

    Note: This function override the default django utility to provide
    custom formatting for Persian users.

    Options for format are listed in: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    """
    # print(value, format, use_l10n)
    if use_l10n is not None and not use_l10n:
        return original_date_format(value, format=format, use_l10n=use_l10n)

    if isinstance(value, datetime.datetime):
        if value.tzinfo:
            ir_value = value.astimezone(irtz)
        else:
            ir_value = irtz.localize(value)
        date_str = persian_date_format(ir_value.date())
        time_str = '{}:{}'.format(ir_value.hour, ir_value.minute)
        if not format or format in ['DATETIME_FORMAT', 'SHORT_DATETIME_FORMAT']:
            return '{}، ساعت {}'.format(date_str, time_str)
        elif format in ['TIME_FORMAT']:
            return time_str
        elif format in ['DATE_FORMAT', 'SHORT_DATE_FORMAT', 'MONTH_DAY_FORMAT']:
            return date_str

    elif isinstance(value, datetime.date):
        if not format:
            nw = ir_now()
            jn = GregorianToJalali(nw.year, nw.month, nw.day)
            jd = GregorianToJalali(value.year, value.month, value.day)
            if jn.jyear != jd.jyear:
                return '{} {} {}'.format(jd.jday, PERSIAN_MONTHS[jd.jmonth], jd.jyear % 100)
            return '{} {}'.format(jd.jday, PERSIAN_MONTHS[jd.jmonth])

    return original_date_format(value, format=format, use_l10n=use_l10n)


formats.date_format = persian_date_format
