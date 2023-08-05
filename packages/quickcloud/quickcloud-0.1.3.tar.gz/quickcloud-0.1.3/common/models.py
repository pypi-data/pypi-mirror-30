#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
import re
from django.db import models
import os
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,  BaseUserManager, AbstractBaseUser,AbstractUser
from zipreader import fileiterator
import re
from bs4 import BeautifulSoup
from django.conf import settings
import qcmaskingcode as qcm

class API_BACKEND(models.Model):
    secret_api = models.CharField(max_length=500, null=False,blank=False,default='123456789')
    secret_username = models.CharField(max_length=500, null=False,blank=False,default=' ')
    secret_password = models.CharField(max_length=500, null=False,blank=False,default=' ')
    url = models.URLField(default='http://localhost/api1')

    nombre = models.CharField(max_length=200, null=False,blank=False,default=' ')
    limit = models.PositiveIntegerField(null=False,blank=False,default=0)
    used = models.PositiveIntegerField(null=False,blank=False,default=0)

    @property
    def left_balance(self):
        return self.limit - self.used

    def __unicode__(self):
        return u'%s %s '% (self.nombre,str(self.limit))


class Contract(User):
    rut = models.CharField(max_length=200, null=True,blank=True)
    nrocontrato = models.CharField(max_length=200, null=True,blank=True,default='1',unique=True)
    empresa = models.CharField(max_length=200, null=True,blank=True)
    api = models.ForeignKey(API_BACKEND)
    limit = models.PositiveIntegerField(null=False,blank=False,default=0)
    used = models.PositiveIntegerField(null=False,blank=False,default=0)
    license = models.CharField(max_length=200, null=True,blank=True,editable=False)

    objects = BaseUserManager()


    def __unicode__(self):
        return 'Empresa: %s - Contrato: %s' % (self.empresa ,self.nrocontrato)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
