#!/usr/bin/env python
# vi: et sw=2 fileencoding=utf-8

from __future__ import unicode_literals

from django.db import models


class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField,self).get_prep_value(value)
        if value:
            return value[:self.max_length]
        return value


class UserRequest(models.Model):
  user = models.IntegerField(null=True)
  timestamp = models.DateTimeField(auto_now_add=True)
  path = TruncatingCharField(max_length=2047)
  method = TruncatingCharField(max_length=255)
  scheme = TruncatingCharField(max_length=255)
  body = models.TextField()
  content_length = TruncatingCharField(max_length=255)
  content_type = TruncatingCharField(max_length=255)
  http_accept = TruncatingCharField(max_length=255)
  http_accept_encoding = TruncatingCharField(max_length=255)
  http_accept_language = TruncatingCharField(max_length=255)
  http_host = TruncatingCharField(max_length=255)
  http_referer = TruncatingCharField(max_length=2047)
  http_user_agent = TruncatingCharField(max_length=255)
  remote_addr = TruncatingCharField(max_length=255)
  remote_host = TruncatingCharField(max_length=255)
  remote_user = TruncatingCharField(max_length=255)
  server_name = TruncatingCharField(max_length=255)
  server_port = TruncatingCharField(max_length=255)
  post_data = models.TextField()
  get_data = models.TextField()
  cookies = models.TextField()
  encoding = TruncatingCharField(max_length=255)
  is_ajax = models.BooleanField()


  # class UserRequest


