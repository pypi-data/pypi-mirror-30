import warnings
import os

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed
from django.utils import six
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django.conf import settings


DJOSER_SETTINGS_NAMESPACE = 'MARKDOCS'

default_settings = {
    'DOC_PATH': settings.BASE_DIR + '/mdocs/',
    'DOC_TITLE': 'Documentation'
}


class Settings(object):
    def __init__(self, default_settings, explicit_overriden_settings=None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = getattr(
            django_settings, DJOSER_SETTINGS_NAMESPACE, {}
        ) or explicit_overriden_settings

        self._load_default_settings()
        self._override_settings(overriden_settings)

    def _load_default_settings(self):
        for setting_name, setting_value in six.iteritems(default_settings):
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings):
        for setting_name, setting_value in six.iteritems(overriden_settings):
            value = setting_value
            setattr(self, setting_name, value)


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)

    def get(self, key):
        """
        This function is here only to provide backwards compatibility in
        case anyone uses old settings interface.
        It is strongly encouraged to use dot notation.
        """
        warnings.warn(
            'The settings.get(key) is superseded by the dot attribute access.',
            PendingDeprecationWarning
        )
        try:
            return getattr(self, key)
        except AttributeError:
            raise ImproperlyConfigured('Missing settings: {}[\'{}\']'.format(
                DJOSER_SETTINGS_NAMESPACE, key)
            )


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    print('hello444')
    global settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)
