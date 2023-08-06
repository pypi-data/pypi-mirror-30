from pydeployer import security

import logging
import json

logger = logging.getLogger(__name__)


def create_user():
    data = {}

    print('Please enter the following information')

    data['ip'] = security.get_input('Remote machine IP\t: ')
    data['name'] = security.get_input('Username\t: ')
    data['pwd'] = security.get_password()

    key = security.get_password("Enter password for encryption (or leave blank):")
    return User(data, key)


def parse_user_file(data):
    while True:
        try:
            pwd = security.get_password()
            new_user = User(data, pwd)
            new_user.decrypt()
            return new_user

        except Exception as e:
            print(e)


class User:
    def __init__(self, data, key):
        self.data = data
        self.key = key

    def decrypt(self):
        status, data_str = security.decrypt(self.data, self.key)
        if not status:
            raise Exception('Password is wrong.')
        self.data = json.loads(data_str)

    def encrypt(self):
        data_str = json.dumps(self.data)
        self.data = security.encrypt(data_str, self.key)

    def read_decrypted(self):
        status, data_str = security.decrypt(self.data, self.key)
        if not status:
            raise Exception('Password is wrong.')
        return json.loads(data_str)

    def read_encrypted(self):
        data_str = json.dumps(self.data)
        return security.encrypt(data_str, self.key)

    def to_string(self):
        return self.read_encrypted().decode('utf-8')
