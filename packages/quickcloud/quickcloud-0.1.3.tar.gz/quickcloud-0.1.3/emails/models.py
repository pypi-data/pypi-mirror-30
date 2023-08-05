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
from common.models import Contract


class ContractEmail(Contract):


    def save(self, *args, **kwargs):
        ingreso = True if self.pk is None else False
        super(ContractEmail, self).save(*args, **kwargs)
        self.nrocontrato = '%09d'%(self.pk)
        self.license = qcm.generate(int(self.nrocontrato))
        super(ContractEmail, self).save(force_update=True)
        if ingreso:
            saldo = SaldoEmails(contractUser=self)
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
        verbose_name = 'Contrato Email'
        verbose_name_plural = 'Contratos Emails'


class EmailSubscriber(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    email = models.EmailField()
    nombre = models.CharField(max_length=200, null=True,blank=True)
    apellido = models.CharField(max_length=200, null=True,blank=True)
    apellido2 = models.CharField(max_length=200, null=True,blank=True)
    telefono = models.CharField(max_length=200, null=True,blank=True)
    rut = models.CharField(max_length=200, null=True,blank=True)
    fecha_nacimiento = models.DateField(null=True,blank=True)
    direccion = models.CharField(max_length=200,null=True,blank=True)
    comuna = models.CharField(max_length=200,null=True,blank=True)


    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'


class BaseDatos(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='emails_contractUser')
    nombre = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        super(BaseDatos, self).save(*args, **kwargs)
        if self.emailbasedatos_set.count()<1:
            newEmailSubscribers = EmailSubscriber.objects.exclude(email__in=[email.email.email for email in EmailBaseDatos.objects.all()]).filter(contractUser=self.contractUser)
            for newEmailSubscriber in newEmailSubscribers:
                emailbd = EmailBaseDatos(email=newEmailSubscriber,contractUser=self.contractUser)
                self.emailbasedatos_set.add(emailbd,bulk=False)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Base de datos de emails'
        verbose_name_plural = 'Bases de datos de emails'


class EmailBaseDatos(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    basedatos = models.ForeignKey(BaseDatos)
    email = models.ForeignKey(EmailSubscriber)

    def __unicode__(self):
        return '%s -> %s'% (self.basedatos.nombre,self.email.email)

    class Meta:
        verbose_name = 'Email en base de datos'
        verbose_name_plural = 'Emails en base de datos'


class EmailTemplate(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    nombre = models.CharField(max_length=200,null=True,blank=True)
    zipFile = models.FileField(upload_to='./adjuntos/')
    subject = models.CharField(max_length=200,null=True,blank=True)
    from_email = models.CharField(max_length=200,null=True,blank=True)

    @property
    def urlZipFile (self):
        if self.zipFile and hasattr(self.zipFile, 'url'):
            u = settings.MEDIA_URL + '/adjuntos/' + os.path.basename(self.zipFile.url)
        else:
            u =''
        return u


    def save(self, *args, **kwargs):
        super(EmailTemplate, self).save(*args, **kwargs)
        self.uncompress()


    def uncompress(self):
        path = settings.MEDIA_ROOT + '/adjuntos/'
        zipfilename = path + os.path.basename(self.zipFile.url)
        path = path +'/zipfile/'+ os.path.basename(self.zipFile.url) + '/'
        os.makedirs(path)
        for filename,content in fileiterator(zipfilename):
            try:
                f= open(path + filename,'w')
                f.write(content)
                f.close()
            except:
                os.makedirs(path + filename)


    @property
    def attachedFiles(self):
        path = settings.MEDIA_ROOT + '/adjuntos/'
        zipfilename = path + os.path.basename(self.zipFile.url)
        pathfile = path +'zipfile/'+ os.path.basename(self.zipFile.url) + '/'
        return [pathfile + filename for (filename,content) in fileiterator(zipfilename)]

    @property
    def htmlContentOuter(self):
        path = settings.MEDIA_ROOT + '/adjuntos/'
        zipfilename = path + os.path.basename(self.zipFile.url)
        path = path +'/zipfile/'+ os.path.basename(self.zipFile.url) + '/'
        f= open(path + 'index.html','r')
        html_content = f.read()
        return html_content

    @property
    def htmlContent(self):
        soup = BeautifulSoup(self.htmlContentOuter)
        images = soup.body.find_all('img')
        for i in range (0,images.__len__()):
            if (not images[i]['src'].startswith('cid:')) and (images[i]['src'].startswith('http://'+settings.ADMIN_DOMAIN) or images[i]['src'].startswith('https://'+settings.ADMIN_DOMAIN)):
                images[i]['src']= 'cid:%s' % os.path.basename(images[i]['src'])
        html_content = soup.body.decode_contents(formatter='html')

        links = soup.body.find_all('a')
        for i in range (0,links.__len__()):
            if not links[i]['href'].startswith('http://%s/q?m=%s&l=' % (settings.ADMIN_DOMAIN,str(self.pk))):
                links[i]['href'] = 'http://%s/q?m=%s&l=%s' % (settings.ADMIN_DOMAIN, str(self.pk),links[i]['href'])
        html_content = soup.body.decode_contents(formatter='html')
        return html_content

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'

class LinkCounter(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    plantilla = models.ForeignKey(EmailTemplate)
    link = models.URLField(max_length=1000)
    clicks = models.FloatField()

    def __unicode__(self):
        return '%s | %s' % (self.plantilla.nombre,self.link)

    class Meta:
        verbose_name = 'Contador de clicks por link'
        verbose_name_plural = 'Contadores de clicks por link'

class Delivery(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    fecha = models.DateTimeField()
    plantilla = models.ForeignKey(EmailTemplate)
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
        phones  = [edb.email for edb in self.basedatos.emailbasedatos_set.filter(contractUser=self.contractUser)]
        for phone in phones:
            dq = DeliveryQueue(email=email,contractUser=self.contractUser)
            self.deliveryqueue_set.add(dq,bulk=False)

    class Meta:
        verbose_name = u'Envío Programado'
        verbose_name_plural = u'Envíos Programados'

ESTADO_DELIVERY = (('ACEPTADO','ACEPTADO'),
                    ('RECHAZADO','RECHAZADO'),
                    )

class DeliveryQueue(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
    delivery = models.ForeignKey(Delivery)
    email = models.ForeignKey(EmailSubscriber)
    enviado = models.NullBooleanField(editable=False,null=True,blank=True)
    estado = models.CharField(choices=ESTADO_DELIVERY,max_length=200,null=True,blank=True,editable=False)


    def __unicode__(self):
        return '%s %s' % (unicode(self.delivery),unicode(self.email))

    @property
    def htmlContent(self):
        return self.delivery.plantilla.htmlContent

    @property
    def plainContent(self):
        html_content = self.htmlContent
        try:
            text_content = re.sub(r'(<!--.*?-->|<[^>]*>)', '', html_content.replace('<br>', '\n').replace('<BR>', '\n').replace('<br/>', '\n'.replace('<BR/>', '\n')))
        except:
            text_content = 'No se puede obtener el contenido del mensaje'
        return text_content

    @property
    def from_email(self):
        return self.delivery.plantilla.from_email if not self.delivery.plantilla.from_email is None else 'admin@quickmail.cl'

    @property
    def subject(self):
        return self.delivery.plantilla.subject if not self.delivery.plantilla.subject is None else '[QuickCloud] Email Message'

    @property
    def attachedFiles(self):
        return self.delivery.plantilla.attachedFiles

    class Meta:
        verbose_name = u'Cola de Envío'
        verbose_name_plural = u'Cola de Envíos'

class SaldoEmails(models.Model):
    contractUser = models.ForeignKey(ContractEmail, verbose_name='Contrato',editable=False,null=True,blank=True,related_name='%(app_label)s_%(class)s_contractUser')
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
        super(SaldoEmails, self).save(*args, **kwargs)

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
        verbose_name = u'Saldo Emails'
        verbose_name_plural = u'Saldo Emails'
