# import re
import ssl
import uuid
# import urllib

# from urllib.parse import ParseResult


class CertificateRead:
    def __init__(self, crt, ca=None):
        self.crt = ssl._ssl._test_decode_cert(crt)
        if ca:
            self.ca = ssl._ssl._test_decode_cert(ca)

    @property
    def network(self):
        return uuid.UUID(self.crt["subject"][0][0][1])

    @property
    def creator(self):
        return uuid.UUID(self.crt["subject"][1][0][1])

    @property
    def endpoint(self) -> str:
        return self.crt['issuer'][0][0][1]

        # return urllib.parse.urlparse(addr)

    @property
    def serial(self):
        return self.crt['serialNumber']

    @property
    def version(self):
        return self.crt['version']

    @property
    def notAfter(self):
        return self.crt['notAfter']
