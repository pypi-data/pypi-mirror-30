#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib
import urllib2,urllib
import gzip
import StringIO
import socket,ssl

class MyHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        self.sock = socket.create_connection((self.host,self.port),self.timeout)

class MyHTTPHandler(urllib2.HTTPHandler):
    def http_open(self,req):
        return self.do_open(MyHTTPConnection,req)

class MyHTTPSConnection(httplib.HTTPSConnection):
    def __init__(self,*args,**kwargs):
        httplib.HTTPSConnection.__init__(self,*args,**kwargs)

    def connect(self):
        sock= socket.create_connection((self.host,self.port),self.timeout)
        if self._tunnel_host:
            self.sock= sock
            self._tunnel()
        try:
            self.sock= ssl.wrap_socket(sock,self.key_file,self.cert_file,ssl_version=ssl.PROTOCOL_TLSv1)
        except ssl.SSLError,e:
            print("TryingSSLv3.")
            self.sock= ssl.wrap_socket(sock,self.key_file,self.cert_file,ssl_version=ssl.PROTOCOL_SSLv3)



class Http:
    def get(self,url,ip=None,ua='',refer='',cookie='',gbk=False,serverIp='',serverPort=''):
        httpClient=None
        try:
            protocol, s1 = urllib.splittype(url)
            host, s2=  urllib.splithost(s1)
            host, port = urllib.splitport(host)
            if port is None:
                if protocol=="http":
                    port = 80
                elif protocol=="https":
                    port = 443

            if not serverIp:
                serverIp=host
            if not serverPort:
                serverPort=port

            if protocol=="https":
                if ip:
                    httpClient = MyHTTPSConnection(serverIp, serverPort, timeout=60,source_address=(ip,0))
                else:
                    httpClient = MyHTTPSConnection(serverIp, serverPort, timeout=60)
            else:
                if ip:
                    httpClient = MyHTTPConnection(serverIp, serverPort, timeout=60,source_address=(ip,0))
                else:
                    httpClient = MyHTTPConnection(serverIp, serverPort, timeout=60)


            if ua=='':
                ua='Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
            headers = {
                "Host":host,
                "User-Agent":ua,
                "Referer":refer,
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.",
                'Accept-Encoding':'gzip,deflate,sdch',
                'Cache-Control':'max-age=0',
            }
            if cookie:
                headers['Cookie']=cookie

            httpClient.request('GET',s2,'',headers)
            response = httpClient.getresponse()
            if response.status==302:
                return 302, response.getheader('location')
            elif response.status==301:
                return 301, response.getheader('location')
            elif response.status==200:
                content=response.read()
                if response.getheader('content-encoding')=='gzip':
                    compressedstream = StringIO.StringIO(content)
                    gzipper = gzip.GzipFile(fileobj=compressedstream)
                    content = gzipper.read()
                if gbk:
                    content=content.decode('gbk','ignore').encode('utf-8')
                return 200,content
            else:
                return response.status,None
        except Exception, e:
            print url
            print e
        finally:
            if httpClient:
                httpClient.close()
        return None,None

    def post(self,url,ip=None,ua='',refer='',cookie='',data={},gbk=False,serverIp='',serverPort=''):
        httpClient=None
        try:
            protocol, s1 = urllib.splittype(url)
            host, s2=  urllib.splithost(s1)
            host, port = urllib.splitport(host)
            if port is None:
                if protocol=="http":
                    port = 80
                elif protocol=="https":
                    port = 443

            if not serverIp:
                serverIp=host
            if not serverPort:
                serverPort=port

            if protocol=="https":
                if ip:
                    httpClient = MyHTTPSConnection(serverIp, serverPort, timeout=60,source_address=(ip,0))
                else:
                    httpClient = MyHTTPSConnection(serverIp, serverPort, timeout=60)
            else:
                if ip:
                    httpClient = MyHTTPConnection(serverIp, serverPort, timeout=60,source_address=(ip,0))
                else:
                    httpClient = MyHTTPConnection(serverIp, serverPort, timeout=60)


            if ua=='':
                ua='Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
            headers = {
                "Host":host,
                "User-Agent":ua,
                "Referer":refer,
                "Content-type": "application/x-www-form-urlencoded",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.",
                'Accept-Encoding':'gzip,deflate,sdch',
                'Cache-Control':'max-age=0'
            }
            if cookie:
                headers['Cookie']=cookie
            params = urllib.urlencode(data)
            httpClient.request('POST',s2,params,headers)
            #response是HTTPResponse对象
            response = httpClient.getresponse()
            #print response.status
            #print response.reason
            if response.status==302:
                return 302, response.getheader('location')
            elif response.status==301:
                return 301, response.getheader('location')
            elif response.status==200:
                content=response.read()
                if response.getheader('content-encoding')=='gzip':
                    compressedstream = StringIO.StringIO(content)
                    gzipper = gzip.GzipFile(fileobj=compressedstream)
                    content = gzipper.read()
                if gbk:
                    content=content.decode('gbk','ignore').encode('utf-8')
                return 200,content
        except Exception, e:
            print e
        finally:
            if httpClient:
                httpClient.close()
        return None,None
