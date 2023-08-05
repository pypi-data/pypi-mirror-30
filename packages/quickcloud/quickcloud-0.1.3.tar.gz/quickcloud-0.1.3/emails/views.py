# Create your views here.
from django.shortcuts import render_to_response
from .models import *
from simplejson.encoder import JSONEncoder
import simplejson
import urllib2
import urllib
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect


@csrf_exempt
def qmView(request):
    m = request.GET['m']
    e = request.GET['e']

    plantilla = EmailTemplate.objects.get(pk=m)
    header_html = '<html><body>'
    footer_html = '</body></html>'
    html_content = '%s%s%s' % (header_html,plantilla.htmlContent.replace('cid:', 'media/adjuntos/zipfile/' + os.path.basename(plantilla.zipFile.path) + '/img/'),footer_html)
    email = Email.objects.get(pk=e)
    nombre = '%s %s' % (email.nombre,email.apellido)

    response = render_to_response('jsonList.html',{'json':html_content},content_type='text/html')
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    response["mimetype"] = "text/html"
    return response

@csrf_exempt
def linkView(request):
    l = request.GET['l']
    m = request.GET['m']

    plantilla = EmailTemplate.objects.get(pk=m)

    linkCounterMatch = LinkCounter.objects.filter(plantilla=plantilla,link=l)[:1]
    if linkCounterMatch.count()>0:
        linkCounter = linkCounterMatch.get()
        linkCounter.clicks+=1
        linkCounter.save()
    else:
        linkCounter = LinkCounter(plantilla=plantilla,link=l,clicks=1)
        linkCounter.save()

    return redirect(l)
