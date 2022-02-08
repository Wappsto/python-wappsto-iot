import random
import uuid
from OpenSSL import crypto


def root_certifi_gen(name: str):

    ca_key = crypto.PKey()
    ca_key.generate_key(crypto.TYPE_RSA, 2048)  # ca_key

    ca_crt = crypto.X509()
    subject = ca_crt.get_subject()
    subject.commonName = name
    ca_crt.set_issuer(subject)
    ca_crt.gmtime_adj_notBefore(0)
    ca_crt.gmtime_adj_notAfter(5*365*24*60*60)
    ca_crt.set_pubkey(ca_key)
    ca_crt.set_serial_number(random.randrange(100000))
    ca_crt.set_version(2)
    ca_crt.add_extensions([
        crypto.X509Extension(
            b'subjectAltName',
            False,
            ','.join([
                f'DNS:{name}',
                f'DNS:*.{name}',
                'DNS:localhost',
                'DNS:*.localhost']).encode()),
        crypto.X509Extension(b"basicConstraints", True, b"CA:false")])

    ca_crt.sign(ca_key, 'SHA256')

    # crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key).decode()
    # ca_key  # Self signed certificate!

    return {
        "ca_crt": ca_crt,
        "ca_key": ca_key
    }


def client_certifi_gen(name: str, uid: uuid.UUID):
    root = root_certifi_gen(name=name)
    client_key = crypto.PKey()
    client_key.generate_key(crypto.TYPE_RSA, 2048)  # client_key
    client_cert = crypto.X509()
    subject = client_cert.get_subject()
    subject.commonName = str(uid)
    client_cert.set_issuer(root.get('ca_crt').get_subject())
    client_cert.gmtime_adj_notBefore(0)
    client_cert.gmtime_adj_notAfter(5*365*24*60*60)
    client_cert.set_pubkey(client_key)

    client_cert.sign(root.get("ca_key"), 'SHA256')

    ca_crt = crypto.dump_certificate(crypto.FILETYPE_PEM, root.get("ca_crt")).decode()
    client_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key).decode()
    client_cst = crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert).decode()

    return (
        ca_crt,
        client_key,
        client_cst
    )
