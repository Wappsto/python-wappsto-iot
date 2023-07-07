"""Contain Certificate helper functions."""
import ssl
import pathlib

from typing import Any
from typing import Dict
from typing import Union


def certificate_info_extraction(crt_path: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """Parse the given certificate into a dictionary."""
    crt: dict = ssl._ssl._test_decode_cert(crt_path)
    crt['issuer'] = {x[0][0]: x[0][1] for x in crt['issuer']}
    crt['subject'] = {x[0][0]: x[0][1] for x in crt['subject']}
    return crt
