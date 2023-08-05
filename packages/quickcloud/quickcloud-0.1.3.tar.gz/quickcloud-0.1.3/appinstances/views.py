# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from .models import *
from simplejson.encoder import JSONEncoder
import simplejson
import urllib2
import urllib
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.db.models import Sum,Count,Avg
import time
import os, tempfile
import pymssql
from datetime import datetime

@csrf_exempt
def IndexView(request):
    items = App.objects.all().exclude(appID__contains='beta').exclude(appID__contains='alpha')
#    items = App.objects.all()
    host = request.get_host()
    return render_to_response('applist.html',{'items': items,'host':host})

@csrf_exempt
def BetaView(request):
    items = App.objects.filter(appID__contains='beta').exclude(appID__contains='alpha')
    host = request.get_host()
    return render_to_response('applist.html',{'items': items,'host':host})

@csrf_exempt
def AlphaView(request):
    items = App.objects.filter(appID__contains='alpha')
    host = request.get_host()
    return render_to_response('applist.html',{'items': items,'host':host})

@csrf_exempt
def app_plist(request,item):
    
    app = App.objects.get(pk=item)
    host = request.get_host()

    return render_to_response('plist.html',{'app': app,'host':host})

@csrf_exempt
def get_app(request):
    item = urllib.unquote(request.GET['id'])
    
    app = App.objects.get(appID=item)
    host = request.get_host()
    application = app.Serialize()
    application['link'] = 'http://%s/%s' % (host,app.appLink)
    
    obj = {'respuesta':'OK',
           'app':application,
           }
    json =  simplejson.dumps(obj,indent=4)
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')

@csrf_exempt
def get_app_2(request,item):
    app = App.objects.get(appID=item)
    host = request.get_host()
    application = app.Serialize()
    application['link'] = 'http://%s/%s' % (host,app.appLink)
    
    obj = {'respuesta':'OK',
           'app':application,
           }
    json =  simplejson.dumps(obj,indent=4)
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')


@csrf_exempt
def get_usuario(request):
    mac = urllib.unquote(request.GET['mac'])
    host = request.get_host()
    try:
        usuario = UsuarioLDAP.objects.filter(macaddress=mac)[:1].get()
    
        obj = {'respuesta':'OK',
               'usuario':usuario.Serialize(),
               }
    except Exception, ex:
        print str(ex)
        obj = {'respuesta':'ERROR',
               'usuario':None,
               }
        
    json =  simplejson.dumps(obj,indent=4)
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')


@csrf_exempt
def save_usuario(request):
    mac = urllib.unquote(request.GET['mac'])
    username = urllib.unquote(request.GET['usuario'])
    host = request.get_host()
    try:
        if UsuarioLDAP.objects.filter(macaddress=mac).count()>1:
            usuario = UsuarioLDAP.objects.get(macaddress=mac)
        else:
            usuario = UsuarioLDAP()
            
        usuario.usuario = username
        usuario.macaddress = mac
        usuario.save()

        obj = {'respuesta':'OK',
               'usuario':usuario.Serialize(),
               }
    except Exception, ex:
        print str(ex)
        obj = {'respuesta':'ERROR',
               'usuario':None,
               }
        
    json =  simplejson.dumps(obj,indent=4)
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')


@csrf_exempt
def FbTabPageView(request):
    m = request.GET['m']
    
    plantilla = IPAFile.objects.get(pk=m)
    meta_header = plantilla.htmlHeader + '<script type="text/javascript" src="https://www.appviasa.com/js/QC_Controls.js"></script>'
    base = 'IPA/zipfile/' + os.path.basename(plantilla.file.path)
    header_html = '<html lang="en"><body> <head> <base href="%s/"/> \
       %s \
    </head>' % (base, meta_header )
    footer_html = '</body></html>'
#    html_content = '%s%s%s' % (header_html,plantilla.htmlContent.replace('cid:', 'ADJUNTOS/zipfile/' + os.path.basename(plantilla.file.path) + '/img/'),footer_html)
    html_content = '%s%s%s' % (header_html,plantilla.htmlContent,footer_html)
#    html_content = html_content.replace('css/', 'IPA/zipfile/' + os.path.basename(plantilla.file.path) + '/css/')
#    html_content = html_content.replace('js/', 'IPA/zipfile/' + os.path.basename(plantilla.file.path) + '/js/')
    
    response = render_to_response('jsonList.html',{'json':html_content},content_type='text/html', mimetype='text/html')
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

@csrf_exempt
def MegustaView(request):
    appID = request.POST.get('appID','generic')
    mg = int(request.POST.get('mg',0))
    nomg = int(request.POST.get('nomg',0))
    l = request.POST.get('l','')
    fecha = datetime.now().date()
    megustaMatch = Megusta.objects.filter(appID=appID,link=l,fecha=fecha)[:1]
    if megustaMatch.count()>0:
        megusta = megustaMatch.get()
        megusta.megusta += mg
        megusta.nomegusta += nomg
        megusta.save()
    else:
        megusta = Megusta()
        megusta.fecha= fecha
        megusta.link=l
        megusta.appID = appID
        megusta.megusta = mg
        megusta.nomegusta = nomg
        megusta.save()
        
    megusta = Megusta.objects.filter(appID=appID,link=l,fecha=fecha)[:1].get()
    obj = {'respuesta':'OK',
           'mg':megusta.megusta,
           'nomg':megusta.nomegusta
           }
    json =  simplejson.dumps(obj,indent=4)
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')

def AppleActivateView(request):
    json =  simplejson.dumps(request,indent=4)
    print json
    return render_to_response('jsonList.html',{'json':json},content_type='application/json')

    