"""ChinaNet Login Tools (JX).

Usage:
 chinanet login <username> <password> [<provice>]
 chinanet logout
 
Examples:
 chinanet login 18888888888 123456
 chinanet login tw152909343 123456 sd
 
Arguments:
 provice - Provice must in:
    sck- 时长卡   zx - 全国中心
    jx - 江西     hn - 湖南     bj - 北京     tj - 天津
    he - 河北     sx - 山西     nm - 内蒙     ln - 辽宁
    jl - 吉林     hl - 黑龙     hb - 湖北     ha - 河南
    js - 江苏     sd - 山东     ah - 安徽     sh - 上海
    zj - 浙江     fj - 福建     gd - 广东     hi - 海南
    gx - 广西     sc - 四川     cq - 重庆     gz - 贵州
    yn - 云南     xz - 西藏     sx - 陕西     gs - 甘肃
    qh - 青海     nx - 宁夏     xj - 新疆     am - 澳门
"""

from docopt import docopt
from bs4 import BeautifulSoup
import requests
import socket
import time

from netportal.chinanet import js_rsa

class ChinaNet(object):
    URL_MAIN = 'http://wlan.ct10000.com/portal4JX/'
    URL_LOGOUT = URL_MAIN + 'CloseNet?userIp={userIp}&basIp=&wlanuserip=';
    URL_LOGIN_OTHER = URL_MAIN + 'OtherUserLogin?account={account}&userPassword={password}&checkCode=&basIp=&wlanuserip=&userIp={userIp}&time={time}"'
    URL_LOGIN_PHONE = URL_MAIN + 'PhoneUserLogin?phoneNumber={phoneNumber}&phonePassword={password}&checkCode=&randServiceCode=&basIp=&wlanuserip=&userIp={userIp}&time={time}"'
    PROVICE = ['sck', 'zx', 'jx', 'hn', 'bj', 'tj', 'he', 'sx', 'nm', 'ln', 'jl', 'hl', 'hb', 'ha', 'js', 'sd', 'ah', 'sh', 'zj', 'fj', 'gd', 'hi', 'gx', 'sc', 'cq', 'gz', 'yn', 'xz', 'sx', 'gs', 'qh', 'nx', 'xj', 'am']
    
    def __init__(self):
        self.__bs = requests.session()
        
    def login(self, username, password, provice=None):
        """Login to ChinaNet"""
        ip = self.__pre_login()
        if provice:
            self.__other_login(username, password, provice, ip)
        else:
            self.__phone_login(username, password, ip)
    
    def __other_login(self, username, password, provice, ip):
        """Login to ChinaNet with username"""
        if provice == "zx":
            username = "{}@wlanwz.zx.chntel.com".format(username)
        else:
            username = "{}@wlan.{}.chntel.com".format(username, provice)
        username = requests.utils.quote(username)
        password = requests.utils.quote(password)
        password = js_rsa.get_rsa_password(password)
        t = str(int(time.time() * 1000))
        url = self.URL_LOGIN_OTHER.format(account=username, password=password, userIp=ip, time=t)
        #print(url)
        page = self.__bs.get(url).text
        page = page.split('#')[0]
        page = page.strip()
        if page == '0':
            print('[+]Success.')
        elif page == '1':
            print('[-]Username or password error.')
        elif page == '2':
            print('[+]User online.')
        elif page == '6':
            print('[-]Portal timeout.')
        else:
            print(page)
        
    def __phone_login(self, phone, password, ip):
        """Login to ChinaNet with phone number"""
        password = requests.utils.quote(password)
        password = js_rsa.get_rsa_password(password)
        t = str(int(time.time() * 1000))
        url = self.URL_LOGIN_PHONE.format(phoneNumber=phone, password=password, userIp=ip, time=t)
        #print(url)
        page = self.__bs.get(url).text
        page = page.strip()
        print(page)
        
    def __pre_login(self):
        """get page support userIp"""
        page = self.__bs.get(self.URL_MAIN).text
        bs = BeautifulSoup(page, 'html.parser')
        return bs.find(attrs={'id' :"userIp"})['value']
     
    def logout(self):
        """ChinaNet logout."""
        url = self.URL_LOGOUT.format(userIp=self.__get_ip())
        #print(url)
        page = self.__bs.get(url).text
        page = page.strip()
        if page == '0':
            print('[+]Success')
        elif page == '-1':
            print('[-]Had been logout')
        else:
            print(page)
        
    def __get_ip(self):
        """Returns: You IPv4."""
        s = socket.socket()
        s.connect(('www.baidu.com',80))
        r = s.getsockname()[0]
        s.close()
        return r

def main():
    """Parse arguments with docopt"""
    args = docopt(__doc__)
    #print(args)
    if args['logout'] == True:
        ChinaNet().logout()
    elif args['login'] == True:
        provice = args['<provice>']
        if provice:
           if not provice in ChinaNet.PROVICE:
               print(__doc__)
               print('[-]Provice chooce errer: {}'.format(provice))
               return None
        ChinaNet().login(args['<username>'], args['<password>'], args['<provice>'])
    else:
        print(__doc__)
    
# for test
if __name__=='__main__':
    main()