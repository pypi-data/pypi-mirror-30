""" Translation module
Use Task.context for get current locale

To set default locale change DEFAULT_LOCALE

Usage:

1. Add translations dirs
    locales_dir = APP_DIR / 'locale'
    set_default_locale(app_config['locale'])
    load_gettext_translations(str(locales_dir), LOCALES_DOMAIN_NAME)

2. Add middleware to application
    app = web.Application(
        debug=app_config['debug'],
        middlewares=[
            babel_middleware(),
        ]
    )

"""
import os
import logging
from typing import Callable

from aiohttp import web
import aiotask_context as context

from babel.support import LazyProxy
from babel.support import Translations
from babel.support import NullTranslations

from babel.core import Locale as _Locale
from babel.core import UnknownLocaleError
import asyncio

DEFAULT_LOCALE = 'en'

logger = logging.getLogger(__name__)


class _GettextTranslations:
    _translations = {}
    _default_locale = DEFAULT_LOCALE
    _supported_locales = frozenset([DEFAULT_LOCALE])

    @property
    def translations(self):
        return self._translations

    @property
    def supported_locales(self):
        return self._supported_locales

    @property
    def default_locale(self):
        return self._default_locale

    def set_default_locale(self, code: str) -> None:
        self._default_locale = code
        self._supported_locales = frozenset(
            list(self._translations.keys()) + [self._default_locale]
        )

    def load_translations(self, directory: str, domain: str) -> None:
        for lang in os.listdir(directory):
            if lang.startswith('.'):
                continue
            if os.path.isfile(os.path.join(directory, lang)):
                continue
            try:
                translation = Translations.load(directory, [lang], domain)
                if lang in self._translations:
                    self._translations[lang].merge(translation)
                else:
                    self._translations[lang] = translation
    
            except Exception as e:
                logging.error("Cannot load translation for '%s': %s", lang, str(e))
                continue
        self._supported_locales = frozenset(
            list(self._translations.keys()) + [DEFAULT_LOCALE])
        logging.info("Supported locales: %s", sorted(self._supported_locales))


_gettext_translations = _GettextTranslations()


def set_default_locale(code: str) -> None:
    _gettext_translations.set_default_locale(code)


def load_gettext_translations(directory: str, domain: str) -> None:
    _gettext_translations.load_translations(directory, domain)


class Locale(_Locale):

    @classmethod
    def get(cls, code: str) -> 'Locale':
        if code not in _gettext_translations.supported_locales:
            code = _gettext_translations.default_locale

        translations = _gettext_translations.translations.get(
            code, NullTranslations()
        )
        locale = cls.parse(code)
        locale.translations = translations
        return locale

    def translate(
        self,
        message: str,
        plural_message: [str, None]=None,
        count: [int, None]=None,
        **kwargs,
    ):
        """ Translate message
        """
        if plural_message is not None:
            assert count is not None
            message = self.translations.ungettext(
                message, plural_message, count)
        else:
            message = self.translations.ugettext(message)

        return message.format(**kwargs) if len(kwargs) else message


def make_lazy_gettext(lookup_func):
    def lazy_gettext(string, *args, **kwargs):
        if isinstance(string, LazyProxy):
            return string

        # disable cache by default, because it can make fluctations
        if 'enable_cache' not in kwargs:
            kwargs['enable_cache'] = False

        return LazyProxy(lookup_func, string, *args, **kwargs)
    return lazy_gettext


def _lookup_func(message, plural_message=None, count=None, **kwargs):
    default_locale = Locale.get(DEFAULT_LOCALE)
    asyncio.Task.current_task
    if asyncio.Task.current_task():
        locale = context.get('locale', default_locale)
    else:
        locale = default_locale
    return locale.translate(message, plural_message, count, **kwargs)


_ = make_lazy_gettext(_lookup_func)


def babel_middleware():

    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)

    async def _babel_middleware(
        app: web.Application, handler: Callable
    ) -> Callable:
        async def _middleware(request: web.Request):
            _code = request.cookies.get('locale', False)
            if not _code:
                locale_code = request.headers.get(
                    'ACCEPT-LANGUAGE', DEFAULT_LOCALE
                )[:2]
                try:
                    context.set('locale', Locale.get(locale_code))
                except (ValueError, UnknownLocaleError):
                    pass
                except Exception as e:
                    raise e
    
            response = await handler(request)
            return response
        return _middleware
    return _babel_middleware
