#!/usr/bin/python
# -*- coding: utf-8 -*-
import demjson
import hashlib
import types
import urllib
from bs4 import BeautifulSoup

def soup(content):
    try:
        soup = BeautifulSoup(content,'html.parser')
        return soup
    except Exception,e:
        print(e)
        return None


def urlencode(word):
    if type(word)==types.UnicodeType:
        word=word.encode('utf-8')
    return urllib.quote(word)

def md5(s):
    if type(s)==types.UnicodeType:
        s=s.encode('utf-8')
    return hashlib.md5(s).hexdigest()

def json_decode(jsonTxt):
    try:
        obj=demjson.decode(jsonTxt)
        return obj
    except Exception,e:
        print(e)
        return None

def json_encode(obj):
    try:
        json_str=demjson.encode(obj)
        return json_str
    except Exception,e:
        print(e)
        return ''
