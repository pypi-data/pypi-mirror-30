"""
Detect network portal type.
"""

import requests
from netportal.chinanet import chinanet
from netportal import cmccweb

def main():
    print(__doc__)
    url = 'http://baidu.com/'
    res = requests.get(url)
    #print(res.url)
    if res.url == url:
        print('[+]Online')
    elif 'wlan.ct10000.com' in res.url:
        print('[+]Use: chinanet (Detected ChinaNet Portal)')
        chinanet.main()
    elif '211.138.211.1:8080' in res.url:
        print('[+]Use: cmccweb (Detected CMCC-WEB Portal)')
        cmccweb.main()
    else:
        print('[-]Unknow network portal')