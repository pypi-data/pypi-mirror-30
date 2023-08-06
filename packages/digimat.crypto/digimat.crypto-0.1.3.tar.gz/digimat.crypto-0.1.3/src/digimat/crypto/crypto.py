import base64
import hashlib

# pip install pycrypto (compiling may fail, see second option below)
# apt-get install python-crypto
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import Blowfish

from itertools import cycle


class AESCipher(object):
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw, b64=True):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        data=iv + cipher.encrypt(raw)
        if b64:
            data=base64.b64encode(data)
        return data

    def decrypt(self, enc, b64=True):
        if b64:
            enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class BlowfishCipher(object):
    def __init__(self, key):
        self._key=key

    def encrypt(self, raw, b64=True):
        try:
            bf=Blowfish.BlowfishCipher(self._key)
            bs=Blowfish.block_size
            psize=bs-divmod(len(raw), bs)[1]
            if psize:
                raw=raw+'\0'*psize
            data=bf.encrypt(raw)
            if b64:
                return base64.b64encode(data)
            return data
        except:
            pass

    def decrypt(self, enc, b64=True):
        try:
            if b64:
                enc=base64.b64decode(enc)
            bf=Blowfish.BlowfishCipher(self._key)
            return bf.decrypt(enc).rstrip()
        except:
            pass


class XORCipher(object):
    def __init__(self, key):
        self._key=key

    # symetric encoding process
    def encode(self, data):
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, cycle(self._key)))

    def encrypt(self, raw, b64=True):
        try:
            data=self.encode(raw)
            if b64:
                return base64.b64encode(data)
            return data
        except:
            pass

    def decrypt(self, enc, b64=True):
        try:
            if b64:
                enc=base64.b64decode(enc)
            return self.encode(enc)
        except:
            pass


if __name__ == "__main__":
    pass
