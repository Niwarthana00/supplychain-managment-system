import hashlib
import json
import os
from time import time
from uuid import uuid4

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        
        # Load chain if exists, else create genesis block
        if os.path.exists('chain.json'):
            self.load_chain()
        else:
            # Create the genesis block
            self.new_block(previous_hash='1', proof=100)

    def load_chain(self):
        try:
            with open('chain.json', 'r') as f:
                self.chain = json.load(f)
        except (ValueError, json.JSONDecodeError):
             self.new_block(previous_hash='1', proof=100)

    def save_chain(self):
        with open('chain.json', 'w') as f:
            json.dump(self.chain, f, indent=4)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        
        self.save_chain()
        
        return block

    def new_transaction(self, sender, recipient, product_id, product_name, quantity, signature=None, public_key=None, **kwargs):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param product_id: <str> ID of the product
        :param product_name: <str> Name of the product
        :param quantity: <int> Quantity of the product
        :param signature: <str> Digital signature of the transaction
        :param public_key: <str> Public key of the sender
        :param kwargs: <dict> Additional transaction data
        :return: <int> The index of the Block that will hold this transaction
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
        }
        transaction.update(kwargs)

        if sender != "0":
            if not signature or not public_key:
                print("Transaction missing signature or public key")
                return False
            
            # Verify signature
            # We reconstruct the exact string that was signed. 
            # Ideally the frontend/caller should pass the data that was signed.
            # Here we assume the caller signed the string representation of the transaction dict BEFORE signature was added.
            from wallet import Wallet
            try:
                # Convert hex signature back to bytes for verification
                signature_bytes = bytes.fromhex(signature)
                if not Wallet.verify_signature(transaction, signature_bytes, public_key):
                    print("Invalid Transaction Signature")
                    return False
            except ValueError:
                print("Signature decoding failed")
                return False
        
        transaction['signature'] = signature
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number 'p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
         :param last_proof: <int>
         :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
