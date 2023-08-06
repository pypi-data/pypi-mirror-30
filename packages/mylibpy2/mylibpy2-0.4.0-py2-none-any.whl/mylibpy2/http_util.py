#-*- coding: utf-8 -*-
import requests as _requests # requests module
from requests.adapters import HTTPAdapter as _HTTPAdapter
from requests.packages.urllib3.util.retry import Retry as _Retry
from . import codec_util
from bs4.element import ResultSet # beautifulsoup4 module
from bs4.element import Tag
from bs4.element import NavigableString

def request(method, url, retry=3, params=None, headers=None, form=None, json=None, allow_redirects=True):
    if type(method) != unicode:
        raise TypeError('method({}) must be unicode!'.format(type(method)))
    if type(url) != unicode:
        raise TypeError('url({}) must be unicode!'.format(type(method)))
    session = _requests.Session()
    retry = _Retry(total=retry, backoff_factor=1.0, status_forcelist=[500, 502, 504])
    adapter = _HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    error = None
    error_message = None
    try:
        resp = session.request(method, url, params=params, headers=headers, json=json, data=form, verify=False, allow_redirects=allow_redirects)
        json = None

        if 'Content-Type' in resp.headers and resp.headers['Content-Type'].find('/json') >= 0:
            json = resp.json()

        return {
            'error': None,
            'method': method,
            'url': resp.url,
            'status_code': resp.status_code,
            'headers': resp.headers,
            'text': resp.text,
            'encoding': resp.encoding,
            'body': resp.content,
            'json': json,
            'history': resp.history
        }
    except _requests.exceptions.ConnectionError as e:
        print dir(e)
        print e
        error = 'ConnectionError'
        error_message = repr(e)
    except _requests.exceptions.HTTPError as e:
        print dir(e)
        print e
        error = 'HTTPError'
        error_message = repr(e)
    except _requests.exceptions.Timeout as e:
        print dir(e)
        print e
        error = 'Timeout'
        error_message = repr(e)
    except _requests.exceptions.TooManyRedirects as e:
        print dir(e)
        print e
        error = 'TooManyRedirects'
        error_message = repr(e)
    except _requests.exceptions.RequestException as e:
        print dir(e)
        print e
        error = 'RequestException'
        error_message = repr(e)
    except Exception as e:
        print dir(e)
        print e
        error = 'Exception'
        error_message = repr(e)

    return { 'error': error, 'error_message': error_message }

def _indent(depth):
    return u'    ' * depth

def _dump_dom(dom, i, strip_text, max_depth, depth=0):
    lines = []
    if isinstance(dom, NavigableString):
        if strip_text:
            lines.append(u'{}[{}] Text({})'.format(_indent(depth), i, dom.strip()))
        else:
            lines.append(u'{}[{}] Text({})'.format(_indent(depth), i, dom.replace(u'\n', u'\\n').replace(u'\t', u'\\t')))
    else:
        lines.append(u'{}[{}] <{}> {} Contents({})'.format(_indent(depth), i, dom.name, dom.attrs, len(dom.contents)))
    
    if depth+1 >= max_depth and isinstance(dom, Tag):
        lines.append(u'{} [.] ...'.format(_indent(depth+1)))
    elif isinstance(dom, Tag):
        for i, d in enumerate(dom.contents):
            lines += _dump_dom(d, i, strip_text, max_depth, depth+1)
    
    return lines

def dump_dom(dom, strip_text=True, max_depth=5):
    lines = []
    if isinstance(dom, ResultSet):
        lines.append(u'bs4.element.ResultSet size({})'.format(len(dom)))
        for i, d in enumerate(dom):
            lines += _dump_dom(d, i, strip_text, max_depth)
    elif isinstance(dom, Tag):
        lines += _dump_dom(dom, 0, strip_text, max_depth)
    else:
        lines.append(codec_util.str_to_unicode(str(dom)))

    return u'\n'.join(lines)


if __name__ == '__main__':
    pass
