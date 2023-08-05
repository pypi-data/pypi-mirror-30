#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import date
from .utils import typeManager
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

class ContractAPI(Contract):

	def save(self, *args, **kwargs):
		ingreso = True if self.pk is None else False
		super(ContractAPI, self).save(*args, **kwargs)
		self.nrocontrato = '%09d'%(self.pk)
		self.license = qcm.generate(int(self.nrocontrato))
		super(ContractAPI, self).save(force_update=True)
		if ingreso:
			saldo = BalanceLimitDeploy(contractUser=self)
			saldo.save(force_insert=True)


	@property
	def left_balance(self):
		return self.limit - self.used

	@property
	def is_available(self):
		return True if self.left_balance>0 and self.api.left_balance>0 else False

	def consume_deploy(self):
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


class AppInstance(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	appName = models.CharField(max_length=200)
	appID = models.CharField(max_length=200,null=True,blank=True)
	appVersion = models.CharField(max_length=200)
	appAuthor = models.CharField(max_length=200)
	icon48 = models.FileField(upload_to='../media/adjuntos/',null=True,blank=True)
	icon57 = models.FileField(upload_to='../media/adjuntos/',null=True,blank=True)
	appType = models.CharField(max_length=100,choices = ( ('0','iOS'),('1','Android'),('2','Desktop'),('3','FB Page Tab'),('4','Python-Django')),null=True,blank=True,default='4' )

	def getFieldNames(self):
		return [field.name for field in self._meta.local_fields]

	@property
	def is_python(self):
		return True if self.appType.__eq__('4') else False


	def Serialize(self):
		fieldValuesPair = [(k,typeManager.force_unicode(unicode(self.serializable_value(k)))) for k in self.getFieldNames()]
		for field in self._meta.many_to_many:
			source = getattr(self, field.attname)
			for item in source.all():
				fieldValuesPair.append((field.attname,item.Serialize()))
		return dict(fieldValuesPair)

	@property
	def appLink(self):
		try:
			ipa = self.ipafile_set.all()[:1].get()
			url = 'IPA/' + os.path.basename(ipa.file.url)
		except:
			url = ''
		return url

	@property
	def appTabLink(self):
		try:
			ipa = self.ipafile_set.all()[:1].get()
			url = 'tabpage?m=%s' % (str(ipa.pk))
		except:
			url = ''
		return url

	@property
	def PublicarEnFB(self):
		if self.appType.__eq__('3'):
			s = '<a href="https://www.facebook.com/dialog/pagetab?app_id=%s&redirect_uri=https://www.appviasa.com/%s">Publicar</a>' % (self.appID,self.appTabLink)
		else:
			s = ''
		return mark_safe(s)

	@property
	def icon48Link(self):
		try:
			url = 'IPA/' + os.path.basename(self.icon48.url)
		except:
			url = ''
		return url

	@property
	def icon57Link(self):
		try:
			url = 'IPA/' + os.path.basename(self.icon57.url)
		except:
			url = ''
		return url

	def __unicode__(self):
		return self.appName

DEFAULT_BASH_COMMAND = 'git reset --hard HEAD\ngit clean -f -d\ngit pull'

class DeployBashTemplate(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	nombre = models.CharField(max_length=200,null=True,blank=True)
	descripcion = models.CharField(max_length=200,null=True,blank=True)
	comando = models.TextField(default=DEFAULT_BASH_COMMAND,help_text='Ejemplo: ' + DEFAULT_BASH_COMMAND)


	def save(self, *args, **kwargs):
		super(DeployBashTemplate, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.nombre

	class Meta:
		verbose_name = 'Plantilla de Comando BASH'
		verbose_name_plural = 'Plantillas de Comandos BASH'

class Delivery(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	fecha = models.DateTimeField()
	plantilla = models.ForeignKey(DeployBashTemplate)
	appinstance = models.ForeignKey(AppInstance)

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
		dq = DeliveryQueue(appinstance=self.appinstance,contractUser=self.contractUser)
		self.deliveryqueue_set.add(dq,bulk=False)

	class Meta:
		verbose_name = u'Envío Programado (Deploy)'
		verbose_name_plural = u'Envíos Programados (Deploy)'

ESTADO_DELIVERY = (('ACEPTADO','ACEPTADO'),
					('RECHAZADO','RECHAZADO'),
					)
class DeliveryQueue(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	delivery = models.ForeignKey(Delivery)
	appinstance = models.ForeignKey(AppInstance,related_name='deliveryappqueue_set')
	enviado = models.NullBooleanField(editable=False,null=True,blank=True)
	estado = models.CharField(choices=ESTADO_DELIVERY,max_length=200,null=True,blank=True,editable=False)

	def __unicode__(self):
		return '%s %s' % (unicode(self.delivery),unicode(self.appinstance))

	@property
	def htmlContent(self):
		return self.delivery.plantilla.comando

	@property
	def plainContent(self):
		html_content = self.htmlContent
		try:
			text_content = re.sub(r'(<!--.*?-->|<[^>]*>)', '', html_content.replace('<br>', '\n').replace('<BR>', '\n').replace('<br/>', '\n'.replace('<BR/>', '\n')))
		except:
			text_content = 'No se puede obtener el contenido del mensaje'
		return text_content


	@property
	def subject(self):
		return self.delivery.plantilla.subject if not self.delivery.plantilla.subject is None else '[QuickCloud] SMS Message'

	@property
	def attachedFiles(self):
		return self.delivery.plantilla.attachedFiles

	class Meta:
		verbose_name = u'Cola de Envío Deploy'
		verbose_name_plural = u'Cola de Envíos Deploy'



class BalanceLimitDeploy(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
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
		super(BalanceLimitDeploy, self).save(*args, **kwargs)

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
		verbose_name = u'Saldo Deploy Disponible'
		verbose_name_plural = u'Saldo Deploy Disponibles'


class IPAFile(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	file = models.FileField(max_length=1000,upload_to='../media/adjuntos/')
	app = models.ForeignKey(AppInstance)

	def save(self, *args, **kwargs):
		super(IPAFile, self).save(*args, **kwargs)
		self.uncompress()

	def uncompress(self):
		path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates') + '/ipa/'
		zipfilename = path + os.path.basename(self.file.url)
		path = path +'/zipfile/'+ os.path.basename(self.file.url) + '/'
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
		path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates') + '/ipa/'
		zipfilename = path + os.path.basename(self.file.url)
		pathfile = path +'zipfile/'+ os.path.basename(self.file.url) + '/'
		return [pathfile + filename for (filename,content) in fileiterator(zipfilename)]

	@property
	def htmlContentOuter(self):
		path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates') + '/ipa/'
		zipfilename = path + os.path.basename(self.file.url)
		path = path +'/zipfile/'+ os.path.basename(self.file.url) + '/'
		f= open(path + 'index.html','r')
		html_content = f.read()
		return html_content

	@property
	def htmlContent(self):
		soup = BeautifulSoup(self.htmlContentOuter)
		images = soup.body.find_all('img')
#		for i in range (0,images.__len__()):
#			if not images[i]['src'].startswith('cid:'):
#				images[i]['src']= 'cid:%s' % os.path.basename(images[i]['src'])
		html_content = soup.body.decode_contents(formatter='html')

		links = soup.body.find_all('a')
		for i in range (0,links.__len__()):
			if not links[i]['href'].startswith('http://'+settings.ADMIN_DOMAIN+'/q?m=%s&l=' % str(self.pk)):
				links[i]['href'] = 'http://'+settings.ADMIN_DOMAIN+'/q?m=%s&l=%s' % (str(self.pk),links[i]['href'])
		html_content = soup.body.decode_contents(formatter='html')
		return html_content

	@property
	def htmlHeader(self):
		soup = BeautifulSoup(self.htmlContentOuter)
		html_content = soup.head.decode_contents(formatter='html')
		return html_content


	def __unicode__(self):
		return self.app.appName



class UsuarioLDAP(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	usuario = models.CharField(max_length=200)
	macaddress = models.CharField(max_length=500)
	def getFieldNames(self):
		return [field.name for field in self._meta.local_fields]


	def Serialize(self):
		fieldValuesPair = [(k,typeManager.force_unicode(unicode(self.serializable_value(k)))) for k in self.getFieldNames()]
		for field in self._meta.many_to_many:
			source = getattr(self, field.attname)
			for item in source.all():
				fieldValuesPair.append((field.attname,item.Serialize()))

		return dict(fieldValuesPair)

	def __unicode__(self):
		return self.usuario

class Megusta(models.Model):
	contractUser = models.ForeignKey(ContractAPI, verbose_name='Contrato',editable=False,null=True,blank=True,related_name="%(app_label)s_%(class)s_related",related_query_name="%(app_label)s_%(class)ss")
	appID = models.CharField(max_length=200,null=True,blank=True)
	fecha = models.DateField(null=True,blank=True)
	link = models.URLField(max_length=1000)
	megusta = models.FloatField(null=True,blank=True)
	nomegusta = models.FloatField(null=True,blank=True)
	clicks = models.FloatField(null=True,blank=True)

	def __unicode__(self):
		return '%s | %s | megusta= %s | nomegusta= %s' % (self.appID,self.link,str(self.megusta),str(self.nomegusta))

	class Meta:
		verbose_name = 'Contador de clicks por link'
		verbose_name_plural = 'Contadores de clicks por link'
