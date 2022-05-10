import ssl
import pathlib

from typing import Union


def certificate_info_extraction(crt_path: Union[str, pathlib.Path]) -> dict:
    crt: dict = ssl._ssl._test_decode_cert(crt_path)
    crt['issuer'] = {x[0][0]: x[0][1] for x in crt['issuer']}
    crt['subject'] = {x[0][0]: x[0][1] for x in crt['subject']}
    return crt
