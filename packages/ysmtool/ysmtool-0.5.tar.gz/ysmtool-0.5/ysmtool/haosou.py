# -*- coding: utf-8 -*-
import http
import re
import tool
from urlparse import urlparse,parse_qs

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
        return status,data


def search(word,page=1):

    myhttp=http.Http()
    url='https://www.so.com/s?ie=utf-8&shb=1&q='+tool.urlencode(word)+"&pn="+str(page)
    status,data = myhttp.get(url=url)
    if status==200:
        soup=tool.soup(data)
        ul=soup.find("ul",{"class":"result"})
        if ul:
            result={"items":[],'page':page}
            i=0
            for item in ul.findAll("li"):
                _item={}
                h3=item.find('h3')
                link=item.find('p',{'class':'res-linkinfo'})
                i+=1
                if not h3 or not link:
                    continue
                _item['title']=h3.text.strip()
                _item['pn']=(page-1)*10+i
                desc=item.find('p',{'class':'res-desc'})
                if desc:
                    _item['desc']=desc.text

                if link:
                    a=link.find('a')
                    url=a.get('href')
                    if url:
                        up=urlparse(url)
                        params=parse_qs(up.query,True)
                        _item['url']=params['u'][0]
                result['items'].append(_item)
            if page==1:
                reg=re.compile(ur'找到相关结果约([0-9,]+)个')
                rematch=reg.search(data.decode('utf-8'))
                if rematch:
                    num=rematch.group(1)
                    num=num.replace(',','')
                    num=long(num)
                    result['total']=num
            return status,result
        else:
            return status,{}
    else:
        return status,data
