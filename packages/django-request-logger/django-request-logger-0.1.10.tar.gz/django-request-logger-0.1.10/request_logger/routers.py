#!/usr/bin/env python
# vi: et sw=2 fileencoding=utf-8


from django.conf import settings

class RequestLoggerRouter(object):


  def db_for_read(self, model, **hints):
    if settings.REQUEST_LOGGER_CONNECTION:
      if model._meta.app_label == 'request_logger':
        return settings.REQUEST_LOGGER_CONNECTION
    return None
    # def db_for_read


  def db_for_write(self, model, **hints):
    if settings.REQUEST_LOGGER_CONNECTION:
      if model._meta.app_label == 'request_logger':
        return settings.REQUEST_LOGGER_CONNECTION
    return None
    # def db_for_write


  def allow_relation(self, obj1, obj2, **hints):
    if settings.REQUEST_LOGGER_CONNECTION:
      if obj1._meta.app_label == 'request_logger' or obj2._meta.app_label == 'request_logger':
        return True
    return None
    # def allow_relation


  def allow_migrate(self, db, app_label, model_name=None, **hints):
    if settings.REQUEST_LOGGER_CONNECTION:
      if app_label == 'request_logger':
          return db == settings.REQUEST_LOGGER_CONNECTION
    return None
    # def allow_migration


  # class AnittaRouter


