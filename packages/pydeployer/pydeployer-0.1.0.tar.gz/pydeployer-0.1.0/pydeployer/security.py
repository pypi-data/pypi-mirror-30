from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import base64
import getpass
import logging
import os

logger = logging.getLogger(__name__)
salt = os.urandom(16)


def get_password(msg="Input your password: "):
    pwd = getpass.getpass(msg)
    return pwd


def get_input(msg):
    return input(msg)


def get_key(pwd):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(pwd)

    return base64.urlsafe_b64encode(digest.finalize())


def encrypt(data, pwd):
    data = data.encode('utf-8')
    pwd = pwd.encode('utf-8')

    f = Fernet(get_key(pwd))
    return f.encrypt(data)


def decrypt(token, pwd):
    token = token.encode('utf-8')
    pwd = pwd.encode('utf-8')

    try:
        f = Fernet(get_key(pwd))
        return True, f.decrypt(token)

    except InvalidToken:
        return False, 0


def read_file(fh):
    data = fh.readline()
    return data
