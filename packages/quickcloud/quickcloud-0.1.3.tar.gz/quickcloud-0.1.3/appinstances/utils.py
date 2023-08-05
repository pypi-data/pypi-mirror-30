# -*- coding: utf-8 -*-

from django.http import HttpResponse
import os

from django.core import exceptions


from django.forms.utils import ErrorList
from django.utils.encoding import force_unicode
from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils.encoding import smart_str


import copy
import datetime

from django.utils.encoding import DjangoUnicodeDecodeError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader


class Unique(object):

    class UniqueTypeError(TypeError):
        """Excepcion especial de transicion
        """
        def __init__(self,*arg,**kwargs):
            super(Unique.UniqueTypeError,self).__init__(*arg,**kwargs)


    def dict(self,s):
        # Try using a dict first, as that's the fastest and will usually
        # work.  If it doesn't work, it will usually fail quickly, so it
        # usually doesn't cost much to *try* it.  It requires that all the
        # sequence elements be hashable, and support equality comparison.
        u = {}
        try:
            for x in s:
                u[x] = 1
        except TypeError, (ex):
            del u  # move on to the next method
            raise Unique.UniqueTypeError(ex)
        else:
            return u.keys()

    def sort(self,s):
        # We can't hash all the elements.  Second fastest is to sort,
        # which brings the equal elements together; then duplicates are
        # easy to weed out in a single pass.
        # NOTE:  Python's list.sort() was designed to be efficient in the
        # presence of many duplicate elements.  This isn't true of all
        # sort functions in all languages or libraries, so this approach
        # is more effective in Python than it may be elsewhere.
        try:
            t = list(s)
            t.sort()
        except TypeError, (ex):
            del t  # move on to the next method
            raise Unique.UniqueTypeError(ex)
        else:
            n=len(s)
            assert n > 0
            last = t[0]
            lasti = i = 1
            while i < n:
                if t[i] != last:
                    t[lasti] = last = t[i]
                    lasti += 1
                i += 1
            return t[:lasti]

    def bruteForce(self,s):
        # Brute force is all that's left.
        u = [x for x in s if not s.count(x)]
        return u

    def sequence(self,s):
        """Return a list of the elements in s, but without duplicates.

        For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
        typeManager.unique("abcabc") some permutation of ["a", "b", "c"], and
        typeManager.unique(([1, 2], [2, 3], [1, 2])) some permutation of
        [[2, 3], [1, 2]].

        For best speed, all sequence elements should be hashable.  Then
        typeManager.unique() will usually work in linear time.

        If not possible, the sequence elements should enjoy a total
        ordering, and if list(s).sort() doesn't raise TypeError it's
        assumed that they do enjoy a total ordering.  Then unique() will
        usually work in O(N*log2(N)) time.

        If that's not possible either, the sequence elements must support
        equality-testing.  Then unique() will usually work in quadratic
        time.
        """
        u = []
        if len(s) > 0:
            try:
                u= unique.dict(s)
            except Unique.UniqueTypeError, (ex):
                try:
                    u = unique.sort(s)
                except Unique.UniqueTypeError, (ex1):
                    u = unique.bruteForce(s)
        return u


class TypeManager(object):

    class EncodingError(Exception):
        """Excepcion especial de codificacion de caracteres
            @attention: Excepcion de transicion por codificacion de caracteres
        """
        def __init__(self,*arg,**kwargs):
            super(TypeManager.EncodingError,self).__init__(*arg,**kwargs)

    def force_unicode(self,s, strings_only=False, errors='strict'):
        u = u''
        for encoding in settings.AVAILABLE_ENCODINGS:
            try:
                u = force_unicode(s, encoding, strings_only, errors)
                return u
            except (DjangoUnicodeDecodeError,UnicodeError, UnicodeEncodeError, UnicodeDecodeError),(ex):
                continue

    def none2Cero(self,param):
        try:
            ret = float(param)
        except:
            ret = 0
            pass
        return ret

    def unique(self,sequence):
        u = unique.sequence(sequence)
        return u

    def timeDelta2Dict(self,delta):
        semanas, dias = divmod(delta.days, 7)
        minutos, segundos = divmod(delta.seconds, 60)
        horas, minutos = divmod(minutos, 60)
        d = {'semanas':semanas,
                              'dias':dias,
                              'horas':horas,
                              'minutos':minutos,
                              'segundos':segundos}
        return d

    def timeDeltaDict2String(self,deltaDict):
        sDelta = u''
        if not (deltaDict is None):
            if (deltaDict['semanas'] > 0):
                sDelta  += u'%s semanas '%(str(deltaDict['semanas']))
            if (deltaDict['dias'] > 0):
                sDelta  += u'%s dï¿½as '%(str(deltaDict['dias']))
            if (deltaDict['horas'] > 0):
                sDelta  += u'%s horas '%(str(deltaDict['horas']))
            if (deltaDict['minutos'] > 0):
                sDelta  += u'%s minutos '%(str(deltaDict['minutos']))
            if (deltaDict['segundos'] > 0 or sDelta == u''):
                sDelta  += u'%s segundos'%(str(deltaDict['segundos']))
        return sDelta

    def timeDelta2String(self,delta):
        deltaDict = self.timeDelta2Dict(delta)
        sDelta = self.timeDeltaDict2String(deltaDict)
        return sDelta

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

unique = Unique()
typeManager = TypeManager()
