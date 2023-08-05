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
from django.contrib.auth.models import User
from zipreader import fileiterator
import re
from bs4 import BeautifulSoup
from django.conf import settings
import qcmaskingcode as qcm
from common.models import Contract

class ContractSMS(Contract):

    def save(self, *args, **kwargs):
        ingreso = True if self.pk is None else False
        super(ContractSMS, self).save(*args, **kwargs)
        self.nrocontrato = '%09d'%(self.pk)
        self.license = qcm.generate(int(self.nrocontrato))
        super(ContractSMS, self).save(force_update=True)
        if ingreso:
            saldo = SaldoSMS(contractUser=self)
            saldo.save(force_insert=True)


    @property
    def left_balance(self):
        return self.limit - self.used

    @property
    def is_available(self):
        return True if self.left_balance>0 and self.api.left_balance>0 else False

    def consume_sms(self):
        self.api.used += 1
        self.api.save(force_update=True)
        self.used += 1
        self.save(force_update=True)

    def __unicode__(self):
        return 'Empresa: %s - Contrato: %s' % (self.empresa ,self.nrocontrato)

    class Meta:
        proxy = True
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'


class PhoneSubscriber(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    phone = models.CharField(max_length=200,default='',help_text='+569######## (Sin +569)')
    email = models.EmailField( null=True,blank=True)
    nombre = models.CharField(max_length=200, null=True,blank=True)
    apellido = models.CharField(max_length=200, null=True,blank=True)
    apellido2 = models.CharField(max_length=200, null=True,blank=True)
    rut = models.CharField(max_length=200, null=True,blank=True)
    fecha_nacimiento = models.DateField(null=True,blank=True)
    direccion = models.CharField(max_length=200,null=True,blank=True)
    comuna = models.CharField(max_length=200,null=True,blank=True)

    def save(self, *args, **kwargs):
        self.phone = re.sub("[^0-9]", "", str(self.phone))
        super(PhoneSubscriber, self).save(*args, **kwargs)


    def __unicode__(self):
        return u'%s %s %s' % (self.nombre,self.apellido,self.phone)

    class Meta:
        verbose_name = 'Suscriptor'
        verbose_name_plural = 'Suscritores'


class BaseDatos(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    nombre = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        super(BaseDatos, self).save(*args, **kwargs)
        if self.phonebasedatos_set.count()<1:
            newPhoneSubscribers = PhoneSubscriber.objects.exclude(phone__in=[phone.phone.phone for phone in PhoneSubscriberBaseDatos.objects.all()]).filter(contractUser=self.contractUser)
            for newPhoneSubscriber in newPhoneSubscribers:
                phonebd = PhoneSubscriberBaseDatos(phone=newPhoneSubscriber,contractUser=self.contractUser)
                self.phonebasedatos_set.add(phonebd,bulk=False)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Base de datos'
        verbose_name_plural = 'Bases de datos'


class PhoneSubscriberBaseDatos(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    basedatos = models.ForeignKey(BaseDatos,related_name='phonebasedatos_set')
    phone = models.ForeignKey(PhoneSubscriber)

    def __unicode__(self):
        return '%s -> %s'% (self.basedatos.nombre,self.phone.phone)

    class Meta:
        verbose_name = 'Telefono en base de datos'
        verbose_name_plural = 'Telefonos en base de datos'


DEFAULT_TEXT_MESSAGE = '{#FROM_PHONE#} te da la bienvenida\n {#NOMBRE#} Ahora eres nuestro nuevo cliente'

class PhoneSubscriberTemplate(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    nombre = models.CharField(max_length=200,null=True,blank=True)
    subject = models.CharField(max_length=200,null=True,blank=True)
    from_phone = models.CharField(max_length=200,null=True,blank=True)
    text_message = models.TextField(default=DEFAULT_TEXT_MESSAGE,help_text='Ejemplo: ' + DEFAULT_TEXT_MESSAGE)


    def save(self, *args, **kwargs):
        super(PhoneSubscriberTemplate, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Plantilla de Mensaje SMS'
        verbose_name_plural = 'Plantillas de Mensaje SMS'

class Delivery(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    fecha = models.DateTimeField()
    plantilla = models.ForeignKey(PhoneSubscriberTemplate)
    basedatos = models.ForeignKey(BaseDatos)

    def __unicode__(self):
        return '%s %s' % (str(self.fecha), self.plantilla.nombre)

    @property
    def enviados(self):
        return self.deliveryqueue_set.filter(enviado=True).count()

    @property
    def aceptados(self):
        return self.deliveryqueue_set.filter(estado='ACEPTADO').count()

    @property
    def rechazados(self):
        return self.deliveryqueue_set.filter(estado='RECHAZADO').count()

    @property
    def pendientes(self):
        return self.deliveryqueue_set.exclude(enviado=True).count()


    def save(self, *args, **kwargs):
        super(Delivery, self).save(*args, **kwargs)
        phones  = [edb.phone for edb in self.basedatos.phonebasedatos_set.filter(contractUser=self.contractUser)]
        for phone in phones:
            dq = DeliveryQueue(phone=phone,contractUser=self.contractUser)
            self.deliveryqueue_set.add(dq,bulk=False)

    class Meta:
        verbose_name = u'Envío Programado'
        verbose_name_plural = u'Envíos Programados'

ESTADO_DELIVERY = (('ACEPTADO','ACEPTADO'),
                    ('RECHAZADO','RECHAZADO'),
                    )
class DeliveryQueue(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',editable=False,null=True,blank=True)
    delivery = models.ForeignKey(Delivery)
    phone = models.ForeignKey(PhoneSubscriber)
    enviado = models.NullBooleanField(editable=False,null=True,blank=True)
    estado = models.CharField(choices=ESTADO_DELIVERY,max_length=200,null=True,blank=True,editable=False)

    def __unicode__(self):
        return '%s %s' % (unicode(self.delivery),unicode(self.phone))

    @property
    def htmlContent(self):
        return self.delivery.plantilla.text_message

    @property
    def plainContent(self):
        html_content = self.htmlContent
        try:
            text_content = re.sub(r'(<!--.*?-->|<[^>]*>)', '', html_content.replace('<br>', '\n').replace('<BR>', '\n').replace('<br/>', '\n'.replace('<BR/>', '\n')))
        except:
            text_content = 'No se puede obtener el contenido del mensaje'
        return text_content

    @property
    def from_phone(self):
        return self.delivery.plantilla.from_phone if not self.delivery.plantilla.from_phone is None else 'admin@quickmail.cl'

    @property
    def subject(self):
        return self.delivery.plantilla.subject if not self.delivery.plantilla.subject is None else '[QuickCloud] SMS Message'

    @property
    def attachedFiles(self):
        return self.delivery.plantilla.attachedFiles

    class Meta:
        verbose_name = u'Cola de Envío SMS'
        verbose_name_plural = u'Cola de Envíos SMS'

class SaldoSMS(models.Model):
    contractUser = models.ForeignKey(ContractSMS, verbose_name='Contrato',unique=True,editable=False,null=True,blank=True)
    left_balance = models.PositiveIntegerField(null=False,blank=False,default=0)
    used = models.PositiveIntegerField(null=False,blank=False,default=0)
    limit = models.PositiveIntegerField(null=False,blank=False,default=0)

    @property
    def licence(self):
        return self.contractUser.license
    def save(self, *args, **kwargs):
        self.left_balance = self.contractUser.left_balance
        self.limit = self.contractUser.limit
        self.used = self.contractUser.used
        super(SaldoSMS, self).save(*args, **kwargs)

    @property
    def saldo(self):
        return self.left_balance
    @property
    def total_contrato(self):
        return self.limit
    @property
    def usado(self):
        return self.used
    class Meta:
        verbose_name = u'Saldo SMS'
        verbose_name_plural = u'Saldo SMS'
