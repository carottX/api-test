#!/usr/bin/env python3

from flask import Flask, request, redirect
import re
import urllib.request as urllib2
import yaml
import copy
import requests
app=Flask(__name__)
header= {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36", "accept": "ext/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3", "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"}

def cfilter(s,pattern):
    y=yaml.safe_load(s)
    res=copy.deepcopy(y)
    res['Proxy']=[]
    res['Proxy Group']=[]
    p=re.compile(pattern)
    cnt1=cnt2=0
    for node in y['Proxy']:
        r=re.search(p,node['name'])
        if r:
            res['Proxy'].append(node)
            cnt2+=1
        else:
            cnt1+=1
    gn=['Rule','Global','DIRECT']
    for node in y['Proxy Group']:
        tmp=copy.deepcopy(node)
        gn.append(tmp['name'])
        tmp['proxies']=[]
        for e in node['proxies']:
            r=re.search(p,e)
            if r or (e in gn):
                tmp['proxies'].append(e)
        res['Proxy Group'].append(tmp)
    s=yaml.dump(res,allow_unicode=True)
    return s

@app.route('/clash',methods=["GET","POST"])
def getdata():
    url=request.args.get("url")
    pattern=request.args.get("re")
    url_re = re.compile(r"((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?")
    if not re.match(url_re,url):
        return 'Wrong url!'
    else:
        req=urllib2.Request(url=url,headers=header)
        resp=urllib2.urlopen(req,timeout=10)
        res=resp.read().decode('utf-8')
        return cfilter(res,pattern=pattern)

cheader={
    'User-Agent':'A lightweighed traffic forwarder'
    }

@app.route('/proxy')
def proxy():
    if not ('url' in request.args):
        return 'An error appeared'
    url = request.args.get('url')
    req=urllib2.Request(url=url,headers=cheader)
    try:
        resp=urllib2.urlopen(req,timeout=10)
        txt=resp.read().decode('utf-8')
    except:
        return 'An error appeared'
    finally:
        return txt

def directlink_1drv(url):
    step1_resp=requests.get(url,allow_redirects=False)
    step1_url=step1_resp.headers['Location']
    step1_url=step1_url.replace('/redir','/download')
    return redirect(step1_url)
    

@app.route('/od')
def onedrive():
    if not ('url' in request.args):
        return 'Missing url'
    url=request.args.get('url')
    if url.startswith('https://1drv.ms'):
        return directlink_1drv(url)
    else:
        return 'Sorry invalid link'

if __name__=='__main__':
    app.run()
