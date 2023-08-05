#!/usr/bin/python3

"""Wifi manager.

Usage:
 wifiman [-i=<iface>] scan
 wifiman [-i=<iface>] list
 wifiman [-i=<iface>] add      <ssid> [<password>]
 wifiman [-i=<iface>] clear
 wifiman [-i=<iface>] connect  <ssid>
 wifiman [-i=<iface>] disconnect
 
Commands:
 scan           Scan wifi.
 list           List profiles.
 add            Add profile.
 clear          Clear all profiles.
 connect        Connect to appointed wifi.
 disconnect     Disconnect. 

Options:
 -i=<iface>         Wifi interface num or name.
 
Examples:
 wifiman -i wlan0 scan
 wifiman -i wlan0 add wifi 1234123
 wifiman -i wlan0 connect wifi
"""

from docopt import docopt
import pywifi
import time

class WifiMan:
    def __init__(self, iface=0):
        ifaces = pywifi.PyWiFi().interfaces()
        if len(ifaces) < 1:
            exit('[-]Not exist wifi interfaces.')
        iface_num = None
        self.__iface = ifaces[0]
        try:
            iface_num = int(iface)
        except:
            pass
        for i, o in enumerate(ifaces):
            if (i == iface_num) or (o.name() == iface):
                self.__iface = o
                print('[**]%s' % o.name())
            else:
                print('[%d]%s' % (i,o.name()))
         
    def scan(self):
        iface = self.__iface
        iface.scan()
        time.sleep(2)
        print('[*]scan results:')        
        last = None
        num = 1
        for i in iface.scan_results():
            if i.ssid == last:
                continue
            last = i.ssid
            print('[%02d]%s' % (num, i.ssid))
            num = num + 1
            
    def list(self):
        iface = self.__iface
        print('[*]profiles:')
        for i, o in enumerate(iface.network_profiles()):
            print('[%02d]%s' % (i, o.ssid))
            
    def add(self, ssid, password=None):
        iface = self.__iface
    
        profile = pywifi.profile.Profile()
        profile.ssid = ssid
        if password:
            profile.auth = pywifi.const.AUTH_ALG_OPEN
            profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
            profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
            profile.key = password
        iface.add_network_profile(profile)
        self.list()
        
    def clear(self):
        iface = self.__iface
        iface.remove_all_network_profiles()
        
    def connect(self, ssid):
        iface = self.__iface
        for i in iface.network_profiles():
            if i.ssid == ssid:
                iface.connect(i)
                return;
        print('[-]Not profile with %s' % ssid)
        
    def disconnect(self):
        self.__iface.disconnect()
        
def main():
    args = docopt(__doc__)
    print(args)
    wifiman = None
    if '-i' in args:
        wifiman = WifiMan(args['-i'])
    else:
        wifiman = WifiMan()
    if args['scan'] == True:
        wifiman.scan()
    elif args['list'] == True:
        wifiman.list()
    elif args['add'] == True:
        wifiman.add(args['<ssid>'], args['<password>'])
    elif args['clear'] == True:
        wifiman.clear()
    elif args['connect'] == True:
        wifiman.connect(args['<ssid>'])
    elif args['disconnect'] == True:
        wifiman.disconnect()
    else:
        print(__doc__)
            
if __name__=='__main__':
    main()