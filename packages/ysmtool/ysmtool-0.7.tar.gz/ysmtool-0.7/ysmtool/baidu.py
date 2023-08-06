# -*- coding: utf-8 -*-
import http
import tool
import types

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

def fengchao(word,cookie,token,userid,eventId,reqid,page=1):
    if type(word)==types.UnicodeType:
        word=word.encode('utf-8')
    # 指定POST的内容
    postData = {
        'params': '{"query":"'+word+'","querySessions":[],"querytype":1,"regions":"1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37","device":0,"rgfilter":1,"entry":"kr_station","planid":"0","unitid":"0","needAutounit":false,"filterAccountWord":false,"attrShowReasonTag":[],"attrBusinessPointTag":[],"attrWordContainTag":[],"showWordContain":"","showWordNotContain":"","pageNo":'+str(page)+',"pageSize":1000,"orderBy":"","order":"","forceReload":true}',
        'path': 'jupiter/GET/kr/word',
        'token': token,
        'userid': userid,
        'eventId':eventId
    }
    myHttp=http.Http()
    url='http://fengchao.baidu.com/nirvana/request.ajax?path=jupiter/GET/kr/word&reqid='+reqid
    status,html=myHttp.post(url,data=postData,cookie=cookie)
    if status==200:
        data=tool.json_decode(html)
        if not data:
            return status,[]
        else:
            if not data.has_key('data') or not data['data']:
                return status,[]
            if  not data['data'].has_key('group') or not data['data']['group']:
                return status,[]
            words=[]
            for word in data['data']['group'][0]['resultitem']:
                _w={}
                _w['word']=word['word']
                _w['kwc']=word['kwc']
                _w['pv']=word['pv']
                _w['pcShow']=word['pvPc']
                _w['wiseShow']=word['pvWise']
                _w['totalWeight']=word['totalWeight']
                _w['showReason']=word['showReason']
                words.append(_w)
            return status,words
    else:
        return status,html
