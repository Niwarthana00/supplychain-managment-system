import hashlib
import json
from time import time
from uuid import uuid4

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.key_pair = RSA.import_key(private_key)
            self.private_key = private_key
            self.public_key = self.key_pair.publickey().export_key().decode('utf-8')
        else:
            self.key_pair = RSA.generate(2048)
            self.public_key = self.key_pair.publickey().export_key().decode('utf-8')
            self.private_key = self.key_pair.export_key().decode('utf-8')

    def sign_transaction(self, transaction):
        private_key = RSA.import_key(self.private_key)
        signer = pkcs1_15.new(private_key)
        h = SHA256.new(str(transaction).encode('utf-8'))
        return signer.sign(h)

    @staticmethod
    def verify_signature(transaction, signature, public_key):
        public_key = RSA.import_key(public_key)
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new(str(transaction).encode('utf-8'))
        try:
            verifier.verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False
