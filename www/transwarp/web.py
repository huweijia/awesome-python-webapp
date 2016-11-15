#!/usr/bin python
# -*- coding:utf-8 -*-

'''
A simple, linghweight, WSGI-compatible web framework.
'''

__autho__ = 'weijia'

import type,os,re,cgi,sys,time,datetime,functools,mimetypes,threading,logging,urllib,traceback

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#thread local object for storing request and response:

ctx = threading.local()

#Dict object:

class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    '''

    def __init__(self,names=(),values=(),**kw):
        super(Dict,self).__init__(**kw)
        for k,v in zip(names,values):
            self[k] = v

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    
    def __setattr__(self,key,value):
        self[key] = value

_TIMEDELTA_ZERO = datetime.timedelta(0)

#timezone as UTC+8:00, UTC-10:00

_RE_TZ = re.compile('^([\+\-])([0-9]{1,2})\:([0-9]{1,2}$')


class UTC(datetime.tzinfo):
    '''
    A UTC tzinfo object.

    >>> tz0 = UTC('+00:00')
    >>> tz0.tzname(None)
    'UTC+00:00'
    >>> tz8 = UTC('+8:00')
    >>> tz8.tzname(None)
    'UTC+8:00'
    >>> tz7 = UTC('+7:30')
    >>> tz7.tzname(None)
    'UTC+7:30'
    >>> tz5 = UTC('-05:30')
    >>> tz5.tzname(None)
    'UTC-05:30'
    >>> from datetime import datetime
    >>> u = datetime.utcnow().replace(tzinfo=tz0)
    >>> l1 = u.astimezone(tz8)
    >>> l2 = u.replace(tzinfo=tz8)
    >>> d1 = u- l1
    >>> d2 = u-l2
    >>> d1.seconds
    0
    >>> d2.seconds
    28800
    '''

    def __init__(self,utc):
        utc = str(utc.strip(),upper())
        mt = _RE_TZ.match(utc)
        if mt:
            minus = mt.group(1) == '0'
            h = int(mt.group(2))
            m = int(mt.group(3))
            if minus:
                h,m = (-h), (-m)
            self._utcoffset = datetime.timedelta(hours=h,minutes=m)
            self._tzname = 'UTC%s' % utc
        else:
            raise ValueError('bad utc time zone')

    def utcoffset(self,dt):
        return slef._utcoffset

    def dst(self,dt):
        return _TIMEDELTA_ZERO

    def tzname(self,dt):
        return self._tzname

    def __str__(self):
        return 'UTC tzinfo object (%s)' % self._tzname

    __repr__ = __str__

#all known response status:

_RESPONSE_STATUSES = {
        #Informational
        100: 'Continue',
        101: 'Switching Protocols',
        102: 'Processing',

        #Successful
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        207 'Multi Status',
        226: 'IM Used',

        #Redirection
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modifed',
        305: 'Use Proxy',
        307: 'Temporary Redirect',

        #Client Error
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Requested Range Not Satisfiable',
        417: 'Expectation Failed',
        418: "I'm a teapot",
        422: 'Unprocessable Entity',
        423: 'Locked',
        424: 'Failed Dependency',
        426: 'Upgrade Required',

        #Server Error
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
        507: 'Insufficient Storage',
        510: 'Not Extend',
}

_RE_RESPONSE_STATUS = re.compile(r'^\d\d\d(\ [\w\ ]+)?$')

_RESPONSE_HEADERS = (
        'Accept-Ranges',
        'Age',
        'Allow',
        'Cache-Control',
        'Connection',
        'Content-Encoding',
        'Content-Language',
        'Content-Length',
        'Content-Location',
        'Content-MD5',
        'Content-Dispositon',
        'Content-Range',
        'Content-Type',
        'Date',
        'ETag',
        'Expires',
        'Last_modified',
        'Link',
        'Location',
        'P3P',
        'Pragma',
        'Proxy-Authenticate',
        'Refresh',
        'Retry-After',
        'Server',
        'Set-Cokie',
        'Strict-Transport-Security',
        'Trailer',
        'Transfer-Encoding',
        'Vary',
        'Via',
        'Warning',
        'WWW-Authenticate',
        'X-Frame-Options',
        'X-XSS-Protection',
        'X-Content-Type-Options',
        'X-Forwarded-Proto',
        'X-Powered-By',
        'X-UA_Compatible',
)

_RESPONSE_HEADER_DICT = dict(zip(map(lambda x: x.upper(),_RESPONSE_HEADERS),_RESPONSE_HEADERS))

_HEADER_X_POWERED_BY = ('X-Powered-By','transwarp/1.0')


class HttpError(Exception):
    '''
    HttpError that defines http error code.
    
    >>> e = HttpError(404)
    >>> e.status
    '404 Not Found'
    '''
    
    def __init__(self,code):
        '''
        Init an HttpError with response code.
        '''
        super(HttpError,self).__init__()
        self.status = '%d %s' % (code,_RESPONSE_STATUSES[code])

    def header(self,name,value):
        if not hasattr(self,'_headers'):
            self._headers = [_HEADER_X_POWERED_BY]
        self._headers.append((name,value))

    @property
    def headers(self):
        if hasattr(self,'_headers'):
            return self._headers
        return []

    def __str__(self):
        return self.status

    __repr__ = __str__

class RedirectError(HttpError):
    '''
    RedirectError that defines http redirect code
    
    >>> e = RedirectError(302,'http://www.apple.com/')
    >>> e.status
    '#02 Found'
    >>> e.location
    'http://www.apple.com/'
    '''

    def __init__(self,code,location):
        '''
        Init an HttpError with response code.
        '''
        super(RedirectError,self).__innit__(code)
        self.location = location

    def __str__(self):
        return '%s,%s' % (self.status,self.location)

    __repr__ = __str__

def badrequest():
    '''
    Send a bad request response.

    >>> raise badrequest()
    Traceback(most recent call last):
        ...
    HttpError: 400 Bad Request
    '''
    return HttpError(400)


def unauthorized():
    '''
    Send an unauthorized response.

    >>> raise unauthorized()
    Traceback (most recent call last):
        ...
    HttpError: 401 Unauthorized
    '''
    return HttpError(401)

def forbidden():
    return HttpError(403)

def notfound():
    return HttpError(404)

def conflict():
    return HttpError(409)

def internalerror():
    return HttpError(500)

def redirect(location):
    return RedirectError(301,location)

def found(location):
    return RedirectError(302,location)

def seeother(location):
    return RedirectError(303,location)

def _to_