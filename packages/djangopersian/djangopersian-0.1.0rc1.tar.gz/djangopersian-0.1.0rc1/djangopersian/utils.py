import pytz
from django.utils.timezone import now


__all__ = ['irtz', 'PERSIAN_MONTHS', 'ir_now', 'ir_today']


irtz = pytz.ir = pytz.timezone('Asia/Tehran')
PERSIAN_MONTHS = [
    '',
    'فروردین', 'اردیبهشت', 'خرداد',
    'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر',
    'دی', 'بهمن', 'اسفند',
]
DIGIT_REPLACEMENTS = [
    ('0', '۰'), ('1', '۱'), ('2', '۲'), ('3', '۳'), ('4', '۴'),
    ('5', '۵'), ('6', '۶'), ('7', '۷'), ('8', '۸'), ('9', '۹'),
]


def ir_now():
    return now().astimezone(pytz.ir)


def ir_today():
    return ir_now().date()


def to_english_str(s):
    if not s:
        return s
    for e, p in DIGIT_REPLACEMENTS:
        s = s.replace(p, e)
    return s
