#!/usr/bin/python
# -*- coding: utf-8 -*-
import tool
import http
from datetime import datetime,timedelta
import re,os

def history(host,se='json'):
    myHttp= http.Http()
    startDate=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    endDate=datetime.now().strftime('%Y-%m-%d')
    cache_name='.cache/aizhan-history-'+host+'-'+startDate+'-'+endDate+'.json'
    json=None
    if os.path.isfile(cache_name):
        jsonTxt=open(cache_name,'r').read()
        json=tool.json_decode(jsonTxt)
    else:
        url="https://lishi.aizhan.com/"+host+"/pcrecordabacklink/"+startDate+"/"+endDate+"/"
        status,html=myHttp.get(url,refer="https://lishi.aizhan.com")
        if status==200:
            regex=re.compile(ur'cc:\'(.*?)\',rn:\'(\d+)\'')
            result=regex.search(html.decode('utf-8'))
            if result:
                cc=result.group(1)
                rn=result.group(2)
                ajaxUrl="https://lishi.aizhan.com/api/hiswave?domain="+host+"&type=pcrecordabacklink&begintime="+startDate+"&endtime="+endDate+"&cc="+cc+"&rn="+rn
                status,jsonTxt=myHttp.get(ajaxUrl,refer="https://lishi.aizhan.com")
                if status==200:
                    json=tool.json_decode(jsonTxt)
                    if json:
                        if not os.path.isdir('.cache'):
                            os.mkdir('.cache')
                        f=open(cache_name,'w')
                        print >>f,jsonTxt

    if json:
        if se and not se=='json':
            print 'date'.ljust(10),se
            for i in range(len(json['date'][se])):
                print json['date'][se][i],json['series'][se][i]
        else:
            return json
