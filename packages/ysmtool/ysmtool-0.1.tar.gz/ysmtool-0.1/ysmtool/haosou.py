# -*- coding: utf-8 -*-
import http
import re

def index(domain):
    reg=re.compile(ur'找到相关结果约([0-9,]+)个')
    myhttp=http.Http()
    url='https://www.so.com/s?ie=utf-8&fr=so.com&src=home-sug-store&q=site%3A'+domain
    status,data = myhttp.get(url=url)
    if status==200:
        result=reg.search(data.decode('utf-8'))
        if result:
            num=result.group(1)
            num=num.replace(',','')
            num=long(num)
            return status,num
        else:
            return status,None
    else:
        return status,None
