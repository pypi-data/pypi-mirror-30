from django.apps import AppConfig
from django.conf import settings


class DjangoPersianAppConfig(AppConfig):
    name = 'djangopersian'
    verbose_name = 'جنگو پارسی'

    def ready(self):
        if not settings.DJANGO_PERSIAN_ENABLED:
            return

        import djangopersian.filters
        from .admin import PersianDateListFilter
        PersianDateListFilter.set_as_default_filter()
