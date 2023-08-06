# -*- coding: utf-8 -*-
import http
import tool

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
        return status,data

def search(word,page=1):
    myhttp=http.Http()
    url='http://www.baidu.com/s?tn=json&rn=10&pn='+str((page-1)*10)+'&wd='+tool.urlencode(word)
    status,data = myhttp.get(url=url,gbk=True)
    if status==200:
        obj=tool.json_decode(data)
        if obj:
            result={'items':[]}
            for item in obj['feed']['entry']:
                if not item:
                    continue
                item['pn']=(page-1)*10+item['pn']
                result['items'].append(item)
            result['total']=obj['feed']['all']
            result['page']=page
            return status,result
        else:
            return status,{}
    else:
        return status,data
