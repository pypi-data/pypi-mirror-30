import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import base64
# import struct

import socket
import fcntl
import struct

from xml.dom import minidom
# import traceback

# pip install pycrypto (compiling may fail, see second option below)
# apt-get install python-crypto
# from Crypto.Cipher import Blowfish
from digimat.crypto import BlowfishCipher


class Utils(object):
    @classmethod
    def getMacAddress(self, ifname='eth0'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            return ''.join(['%02x-' % ord(char) for char in info[18:24]])[:-1]
        except:
            pass

    @classmethod
    def getInterfaceIpAddress(self, ifname='eth0'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
                )[20:24])
        except:
            pass


class CryptedWebservice(object):
    def __init__(self, url, device, key):
        self._url=url
        self._device=device
        self._key=key
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def encrypt(self, data):
        try:
            bf=BlowfishCipher(self._key)
            # bf=Blowfish.BlowfishCipher(self._key)
            # bs=Blowfish.block_size
            # psize=bs-divmod(len(data), bs)[1]
            # if psize:
            #    data=data+'\0'*psize
            # return base64.b64encode(bf.encrypt(data))
            return bf.encrypt(data)
        except:
            pass

    def decrypt(self, data):
        try:
            bf=BlowfishCipher(self._key)
            # bf=Blowfish.BlowfishCipher(self._key)
            # return bf.decrypt(base64.b64decode(data)).rstrip()
            return bf.decrypt(data)
        except:
            pass

    def do(self, command, data=None):
        payload={'device': self._device, 'command': command}
        if data:
            cdata=self.encrypt(data)
            payload['data']=cdata
        try:
            r=requests.post(self._url, verify=False, params=payload, timeout=10)
            if r.status_code==200:
                # print r.text.encode('utf-8')
                try:
                    data=self.decrypt(r.text).strip()
                    # print data
                    return minidom.parseString(data).documentElement
                except:
                    pass
        except:
            pass

    def isResponseSuccess(self, xresponse):
        try:
            if xresponse:
                node=xresponse.firstChild
                while node:
                    if node.nodeType==minidom.Node.ELEMENT_NODE:
                        name=node.nodeName.lower()
                        if name=='success':
                            return node
                    node=node.nextSibling
        except:
            # traceback.print_exc()
            pass

    def doAndCheckSuccess(self, command, data):
        xresponse=self.do(command, data)
        return self.isResponseSuccess(xresponse)

    def ping(self):
        xresponse=self.do('ping')
        if self.isResponseSuccess(xresponse):
            return True
