from typing import NamedTuple, Any, Callable, Optional, overload, Dict, List
import cgi
import json
import os
import gzip
import requests
from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
from http.cookies import Morsel, SimpleCookie, CookieError
from urllib.parse import unquote, quote

from io import BytesIO

from lessweb.storage import Storage
from lessweb.webapi import UploadedFile, HttpError, mimetypes, hop_by_hop_headers
from lessweb.utils import _nil, fields_in_query


def _process_fieldstorage(fs):
    if isinstance(fs, list):
        return _process_fieldstorage(fs[0])  # 递归计算
    elif fs.filename is None:  # 非文件参数
        return fs.value
    else:  # 文件参数
        return UploadedFile(fs)


def _dictify(fs):
    # hack to make input work with enctype='text/plain.
    if fs.list is None:
        fs.list = []
    return dict([(k, _process_fieldstorage(fs[k])) for k in fs.keys()])


class Context(object):
    """
    Contextual variables:
        * environ a.k.a. env – a dictionary containing the standard WSGI environment variables
        * home – the base path for the application, including any parts "consumed" by outer applications
        * homedomain – ? (appears to be protocol + host)
        * homepath – The part of the path requested by the user which was trimmed off the current app. That is homepath + path = the path actually requested in HTTP by the user. E.g. /admin This seems to be derived during startup from the environment variable REAL_SCRIPT_NAME. It affects what web.url() will prepend to supplied urls. This in turn affects where web.seeother() will go, which might interact badly with your url rewriting scheme (e.g. mod_rewrite)
        * host – the hostname (domain) and (if not default) the port requested by the user. E.g. example.org, example.org:8080
        * ip – the IP address of the user. E.g. xxx.xxx.xxx.xxx
        * method – the HTTP method used. E.g. POST
        * path – the path requested by the user, relative to the current application. If you are using subapplications, any part of the url matched by the outer application will be trimmed off. E.g. you have a main app in code.py, and a subapplication called admin.py. In code.py, you point /admin to admin.app. In admin.py, you point /stories to a class called stories. Within stories, web.ctx.path will be /stories, not /admin/stories.
        * protocol – the protocol used. E.g. https
        * query – an empty string if there are no query arguments otherwise a ? followed by the query string.
        * fullpath a.k.a. path + query – the path requested including query arguments but not including homepath.

        e.g. GET http://localhost:8080/api/hello/echo?a=1&b=2
            host => localhost:8080
            protocol => http
            homedomain => http://localhost:8080
            homepath => /api
            home,realhome => http://localhost:8080/api
            ip => 127.0.0.1
            method => GET
            path => /hello/echo
            query => a=1&b=2
            fullpath => /hello/echo?a=1&b=2

        lessweb use ctx.path in routing.
    """
    def __init__(self, app=None) -> None:
        self.status_code: int = 200
        self.reason: str = 'OK'
        self.headers: Dict = {}
        self.app_stack: List = []
        self.app = app
        self.view = None
        self.querynames = None

        self.url_input: Dict = {}
        self.json_input: Optional[Dict] = None
        self._post_data: Optional[Dict] = None
        self._fields: Optional[Dict] = None
        self._pipe: Storage = Storage()

        self.environ: Dict = {}
        self.env: Dict = {}
        self.host: str = ''
        self.protocol: str = ''
        self.homedomain: str = ''
        self.homepath: str = ''
        self.home: str = ''
        self.realhome: str = ''
        self.ip: str = ''
        self.method: str = ''
        self.path: str = ''
        self.query: str = ''
        self.fullpath: str = ''

    def __call__(self):
        return self.app_stack[-1](self)

    def set_param(self, realname, realvalue):
        self._pipe[realname] = realvalue

    def get_param(self, realname, default=None):
        return self._pipe.get(realname, default)

    def set_header(self, header, value):
        """
        Example:

        """
        assert isinstance(header, str) and isinstance(value, str)
        if '\n' in header or '\r' in header or '\n' in value or '\r' in value:
            raise ValueError('invalid characters in header')
        self.headers[header] = value

    def get_header(self, header, default=None):
        """
        Example:

        """
        key = 'HTTP_' + header.replace('-', '_').upper()
        return self.env.get(key, default)

    def is_json_request(self):
        return self.json_input is not None or \
               'json' in self.env.get('CONTENT_TYPE', '').lower()

    @property
    def field_input(self):
        if self.json_input is not None:
            return self.json_input
        if self._fields is not None:
            return self._fields
        if self.is_json_request():
            try:
                self.json_input = json.loads(self.data().decode(self.app.encoding))
            except:
                self.json_input = {'__error__': 'invalid json received'}
            return self.json_input
        else:
            try:
                if self.method in ['HEAD', 'DELETE']:
                    self._fields = fields_in_query(self.query)
                    return self._fields

                # cgi.FieldStorage can raise exception when handle some input
                if self.method == 'GET':
                    _ = cgi.FieldStorage(environ=self.env.copy(), keep_blank_values=1)
                else:
                    fp = BytesIO(self.data())
                    _ = cgi.FieldStorage(fp=fp, environ=self.env.copy(), keep_blank_values=1)
                self._fields = _dictify(_)
            except:
                self._fields = {'__error__': 'invalid fields received'}
        return self._fields

    def data(self) -> bytes:
        """
        Example:

        """
        if self._post_data is not None:
            return self._post_data
        try:
            cl = int(self.env.get('CONTENT_LENGTH'))
        except:
            cl = 0
        self._post_data = self.env['wsgi.input'].read(cl)
        return self._post_data

    def get_input(self, queryname, default=None):
        """
        Example:

        """
        if self.querynames is not None and queryname not in self.querynames:
            return _nil

        ret = self.url_input.get(queryname, _nil)
        if ret is not _nil:
            return ret

        return self.field_input.get(queryname, default)

    def static_file(self, path, basepath='./static', max_age=900, enable_gzip=False):
        """
        Example:

        """
        if '..' in basepath:
            raise HttpError(404, 'not found')
        fullpath = os.path.join(basepath, path)
        try:
            data = open(fullpath, 'rb').read()
            modify_stamp = os.path.getmtime(fullpath)
        except:
            raise HttpError(404, 'not found')
        if enable_gzip and 'gzip' in self.get_header('Accept-Encoding'):
            self.set_header('Content-Encoding', 'gzip')
            data = gzip.compress(data)
        expire_at = datetime.now() + timedelta(seconds=max_age)
        expire_stamp = mktime(expire_at.timetuple())
        self.set_header('Cache-Control', 'max-age=%d' % max_age)
        self.set_header('Expires', format_date_time(expire_stamp))
        self.set_header('Last-Modified', format_date_time(modify_stamp))
        suffix = (path.rsplit('/', 1)[-1] if '/' in path else path)
        if '.' in suffix:
            suffix = suffix.rsplit('.', 1)[-1]
            if suffix in mimetypes:
                self.set_header('Content-Type', mimetypes[suffix])
        return data

    def static_proxy(self, dist_host, fullpath=None):
        headers = {}
        for wsgi_key, value in self.env.items():
            if wsgi_key.startswith('HTTP_'):
                headers[wsgi_key[5:].replace('_', '-')] = value
        if fullpath is None:
            fullpath = self.fullpath
        conn = requests.get(dist_host + fullpath, headers=headers)
        resp_headers = {k: v for k, v in conn.headers.items() if k not in hop_by_hop_headers}
        self.headers.update(resp_headers)
        if conn.status_code > 299:
            raise HttpError(conn.status_code, conn.text, self.headers)
        return conn.content

    def set_cookie(self, name, value, expires='', domain=None, secure=False, httponly=False, path=None):
        """Set a cookie."""
        morsel = Morsel()
        morsel.set(name, value, quote(value))
        if isinstance(expires, int) and expires < 0:
            expires = -1000000000
        morsel['expires'] = expires
        morsel['path'] = path or self.homepath + '/'
        if domain: morsel['domain'] = domain
        if secure: morsel['secure'] = secure
        value = morsel.OutputString()
        if httponly: value += '; httponly'
        self.set_header('Set-Cookie', value)

    def get_cookie(self):
        """Get cookies --> Dict"""
        http_cookie = self.get_header('cookie', '')
        cookie = SimpleCookie()
        try:
            cookie.load(http_cookie)
        except CookieError:
            cookie = SimpleCookie()
            for attr_value in http_cookie.split(';'):
                try:
                    cookie.load(attr_value)
                except CookieError:
                    pass
        cookies = dict([(k, unquote(v.value)) for k, v in cookie.items()])
        return cookies

    # ~class Context
