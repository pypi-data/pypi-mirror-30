#!/usr/bin/python3
"""CMCC-WEB Web Portal Login.

Usage:
 cmccweb login <username> <password>
 cmccweb logout
 cmccweb getpassword <username>
"""
from docopt import docopt

from bs4 import BeautifulSoup
import requests
import re
import os

class CmccWeb(object):
    URL_MAIN = 'http://211.138.211.1:8080/'
    URL_LOGIN = URL_MAIN + 'cmcclogin.do'
    URL_GET_PASSWORD = URL_MAIN + 'generateDynamicPWD.do'
        
    def login(self, username, password):
        """Login to CMCC-WEB."""
        bs = requests.session()
        
        post_data = self.__get_post_data__(bs, username, password)
       
        page = bs.post(self.URL_LOGIN, data=post_data).text
        
        bs = BeautifulSoup(page, 'html.parser')

        #print('[*]login return page[:256]: \n%s' % page[:256].split())
        
        if u'用户已经在线' in page:
            print('[+]User online.')
            return 1
        if u'计时器' in page:
            print('[+]Success.')
            url = re.findall(r'\"(.+?logout\.do.+?)\"', page)[0]
            with open(self.__get_file(), 'w') as file:
                file.write(url)
            #print(url)
            return 0
        if u'用户名或密码' in page:
            print('[-]Username or password error.')
            return -1
        if u'验证码错误' in page:
            print('[-]Password error.')
            return -2
        if u'用户未开通WLAN业务' in page:
            print('[-]User do not open WLAN Business.')
            return -3   
        print('[-]Unknow error.')
        return -4
        
    def __get_post_data__(self, bs, username, password):
        """Get login post data"""
        page = bs.get(self.URL_MAIN).text
        bs = BeautifulSoup(page, 'html.parser')
        
        loginmode = bs.find(attrs={'name' :"loginmode"})['value']
        wlanacip = bs.find(attrs={'name' :"wlanacip"})['value']
        wlanacname = bs.find(attrs={'name' :"wlanacname"})['value']
        wlanuserip = bs.find(attrs={'name' :"wlanuserip"})['value']
        wlanacssid = bs.find(attrs={'name' :"wlanacssid"})['value']
        portion = bs.find(attrs={'name' :"portion"})['value']
        uaId = bs.find(attrs={'name' :"uaId"})['value']
        #obsReturnAccount = bs.find(attrs = {'name' :"obsReturnAccount"})['value']
        Token = bs.find(attrs={'name' :"Token"})['value']
        #CSRFToken_HW = bs.find(attrs = {'name' :"CSRFToken_HW"})
        
        data = {
            'bpssUSERNAME' : username,
            'textpwd' : '', 
            'bpssBUSPWD' : password,
            'loginmode' : loginmode,
            'wlanacip' : wlanacip,
            'wlanacname' : wlanacname,
            'wlanuserip' : wlanuserip,
            'wlanacssid' : wlanacssid,
            'portion' : portion,
            'uaId' : uaId,
            'obsReturnAccount' : '',
            'Token' : Token
        }
        return data
            
    def get_password(self, username):
        """Get dynamic password"""
        page = requests.post(self.URL_GET_PASSWORD, data={"username":username}).text
        print('[*]Message: ' + page)

    def logout(self):
        """Logout CMCC-WEB."""
        with open(self.__get_file(), 'r') as file:
            url = file.read()
            page = requests.get(url).text.strip()
            if 'SUCCESS' in page:
                print('[+]Success')
            else:
                print(page)
        
    def __get_file(self):
        """Get home file path."""
        parent = None
        if os.name == 'nt':
            parent = os.environ['USERPROFILE'] + '\\netportal\\'
        else:
            parent = os.environ['HOME'] + '/netportal/'
        if not os.path.isdir(parent):
            os.mkdir(parent)
        return parent + 'cmccweb'

def main():
    """Parse arguments with docopt."""
    args = docopt(__doc__)
    #print(args)
    if args['login'] == True:
        CmccWeb().login(args['<username>'], args['<password>'])
    elif args['logout'] == True:
        CmccWeb().logout()
    elif args['getpassword'] == True:
        CmccWeb().get_password(args['<username>'])
    else:
        print(__doc__)   
        
if __name__ == '__main__':
    main()