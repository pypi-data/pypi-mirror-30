from base64 import b64encode
from vital.security import randkey


__all__ = ('Encryption',)


class Encryption(dict):
    '''
    "Encryption":{
       "Mode":"S3|S3-AWS-KMS|AES-CBC-PKCS7|AES-CTR|AES-GCM",
       "Key":"encrypted and base64-encoded encryption key",
       "KeyMd5":"base64-encoded key digest",
       "InitializationVector":"base64-encoded initialization vector"
    }
    '''
    def __init__(self, mode, secret, digest=None, iv=None):
        super(Encryption, self).__init__(Mode=mode, Key=key, KeyMd5=digest,
                                         InitializationVector=iv)

    def set_iv(self, iv=None):
        self['InitializationVector'] = iv or self.generate_secret(128)

    def generate_secret(self, bits=256):
        return b64encode(randkey(bits))
