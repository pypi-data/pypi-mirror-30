#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.encoding import DjangoUnicodeDecodeError
import logging
import os.path

LOGFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../log/custom-error.log')

logging.basicConfig(
    level=logging.NOTSET,
    format=u'%(asctime)s %(levelname)-8s %(message)s'.encode('utf-8'),
    datefmt=u'%m-%d %H:%M',
    #change as needed
#    filename=LOGFILE, 
    filemode='a'
)
logging.getLogger('').setLevel(logging.NOTSET)

def warning(*arg,**kwargs):
    logging.warn(*arg,**kwargs)

def desactivateDebug():
    logging.disable(logging.DEBUG)
def activateDebug():
    logging.getLogger('').setLevel(logging.DEBUG)

class CustomDebug(object):
    def off(self):
        desactivateDebug()
    def on(self):
        activateDebug()
    def write(self,prnt):
        if settings.DEBUG:
            warning(prnt)
debug = CustomDebug()


class TypeManager(object):
    """
    @author: Jean Machuca (Dec 16, 2009)
    """
    class EncodingError(Exception):
        """Especial EncodingError exception. 
        Occurs when an un-existent charset is present in input string
        """
        def __init__(self,*arg,**kwargs):
            super(TypeManager.EncodingError,self).__init__(*arg,**kwargs)
        
    def force_unicode(self,s, strings_only=False, errors='strict'):
        """ Fix unicode string convertion by tuple charset list
        Usage: In your settings.py, type:
        
        AVAILABLE_ENCODINGS = ('ascii','utf-8','latin-1') #for example

    In this example, the string is attempt to be encoded in ascii format, 
    then, if it fails, is attempt to be encoded in utf-8. For last, if all fails,
    the latin-1 format is attempt to be encoded.

    The tuple must be ordered for the minor to major character set. Example:
    The latin-1 charset contains utf-8 and utf-8 contains ascii, then the tuple is 
    ('ascii','utf-8','latin-1'). If another charset is needed (as well as 'utf-16'
    that contains 'utf-8' and it's bigger than 'latin-1') then the tuple is
    ('ascii','utf-8','latin-1','utf-16')
    
    When the correct unicode charsets are setted in settings.AVAILABLE_ENCODINGS, 
    your unicode problems are fixed !

    Enjoy !
        
        """
        
        u = u''
        for encoding in settings.AVAILABLE_ENCODINGS:
            try:
                u = self.force_unicode(s, encoding, strings_only, errors)
                return u
            except (DjangoUnicodeDecodeError,UnicodeError, UnicodeEncodeError, UnicodeDecodeError),(ex):
                debug.write( u'Trying to fix encoding problem: %s'%str(ex))
                continue



class UnicodeFixer(object):
    """
    @author: Jean Machuca (Dec 16, 2009)

    Django Model Overload for PyAMF encoding fix

    Usage: 
        In your model:
        class YourNewModel(UnicodeFixer,models.Model):
            ...
    """
    
    
    def __repr__(self):
        """ repr() function overloaded. PyAMF unicode problems fixing
        """

        try:
            typeManager = TypeManager()
            ret = typeManager.force_unicode(unicode(self))
        except (UnicodeEncodeError, UnicodeDecodeError,UnicodeError), (ex):
            ret = u'[BAD UNICODE]'
            raise TypeManager.EncodingError (str(ex))

    #Fix all non-converted characters for dumping correctly the string data 
        from encodings import normalize_encoding
        return normalize_encoding(ret)