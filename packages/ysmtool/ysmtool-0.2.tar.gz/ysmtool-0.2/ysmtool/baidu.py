# -*- coding: utf-8 -*-
import http

def index(domain):
    myhttp=http.Http()
    url='https://www.baidu.com/s?tn=newsnexpro&wd=site:'+domain
    status,data = myhttp.get(url=url,gbk=True)
    if status==200:
        if data.startswith('num='):
            num=data.split('\n')[0][4:]
            if num:
                return status,long(num)
            else:
                return status,None
    else:
        return status,None
