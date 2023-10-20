import base64
import hashlib
import hmac
import os
import time
import requests

class AcrCloud:

    def __init__(self,access_key, access_secret, req_url) -> None:
        self.access_key = access_key
        self.access_secret = access_secret
        self.req_url = req_url
    

    def recognize(self, filepath):
        http_method = "POST"
        http_uri = "/v1/identify"
        # default is "fingerprint", it's for recognizing fingerprint, 
        # if you want to identify audio, please change data_type="audio"
        data_type = "audio"
        signature_version = "1"
        timestamp = time.time()

        string_to_sign = http_method + "\n" + http_uri + "\n" + self.access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)

        sign = base64.b64encode(hmac.new(self.access_secret.encode('ascii'), string_to_sign.encode('ascii'), digestmod=hashlib.sha1).digest()).decode('ascii')

        # suported file formats: mp3,wav,wma,amr,ogg, ape,acc,spx,m4a,mp4,FLAC, etc
        # File size: < 1M , You'de better cut large file to small file, within 15 seconds data size is better
        f = open(filepath, "rb")
        sample_bytes = os.path.getsize(filepath)

        files = [
            ('sample', ('test.mp3', open(filepath, 'rb'), 'audio/mpeg'))
        ]
        data = {
            'access_key': self.access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version
        }

        r = requests.post(self.req_url, files=files, data=data)
        r.encoding = "utf-8"
        return r.status_code, r.json