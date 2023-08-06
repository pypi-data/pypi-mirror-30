import onetimepass as otp
import json
import cryptography.fernet
import argon2
import base64
import os
import copy

_salt = "V5RlhpuwACffXuUNLex7Al9ulPy4SRHbyaAxWigjX9Z01OVaCO"


def get_default_salt():
    return copy.deepcopy(_salt)


def encrypt_data(data_bytes, password, salt):
    password_hash = argon2.argon2_hash(password=password, salt=salt)
    encoded_hash = base64.urlsafe_b64encode(password_hash[:32])
    encryptor = cryptography.fernet.Fernet(encoded_hash)
    return encryptor.encrypt(data_bytes)


def decrypt_data(cipher_bytes, password, salt):
    password_hash = argon2.argon2_hash(password=password, salt=salt)
    encoded_hash = base64.urlsafe_b64encode(password_hash[:32])
    decryptor = cryptography.fernet.Fernet(encoded_hash)
    return decryptor.decrypt(cipher_bytes)


def write_keys_to_file(auth_keys, password, file_name="data.dat"):
    backup_file = file_name + ".bak"
    if os.path.exists(file_name):
        os.rename(file_name, backup_file)
    with open(file_name, 'wb') as f:
        f.write(encrypt_data(auth_keys.dump_data().encode('utf-8'), password, _salt))
        if os.path.exists(backup_file):
            os.remove(backup_file)


def read_keys_from_file(password, file_name="data.dat"):
    with open(file_name, 'rb') as f:
        ciphered_data = f.read()
        readable_data = decrypt_data(ciphered_data, password, _salt)
        keys_object = AuthenticatorKeys()
        keys_object.read_dump(readable_data.decode('utf-8'))
        return keys_object


class AuthenticatorKeys:
    def __init__(self):
        self.data = {'secrets': {},
                     'version': '1.0'}

    def set_secret(self, name, secret):
        self.data['secrets'][name] = {'secret': secret}

    def get_secret(self, name):
        return self.data['secrets'][name]['secret']

    def get_token(self, name):
        return otp.get_totp(self.get_secret(name))

    def remove_secret(self, name):
        del self.data['secrets'][name]

    def get_names(self):
        return self.data['secrets'].keys()

    def get_size(self):
        return len(self.data['secrets'])

    def dump_data(self):
        return json.dumps(self.data)

    def read_dump(self, dump_data):
        self.data = json.loads(dump_data)

    @staticmethod
    def test_secret_validity(secret):
        otp.get_totp(secret)
