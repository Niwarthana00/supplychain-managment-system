from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from wallet import Wallet
from blockchain import Blockchain
from analytics import generate_plots
import json
import os
import hashlib
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Instantiate the Blockchain
blockchain = Blockchain()
node_identifier = str(uuid4()).replace('-', '')

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        phone = request.form['phone']

        if email in users:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        new_wallet = Wallet()
        
        users[email] = {
            'fullname': fullname,
            'password_hash': password_hash,
            'role': role,
            'phone': phone,
            'public_key': new_wallet.public_key,
            'private_key': new_wallet.private_key
        }
        save_users(users)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users.get(email)
        if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
            session['email'] = email
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        chain = blockchain.chain
        chain_length = len(chain)
        total_transactions = sum(len(block['transactions']) for block in chain)
        latest_block = blockchain.last_block
        
        analytics_data = generate_plots(chain)

        return render_template('dashboard.html', 
                               role=session['role'],
                               chain_length=chain_length,
                               total_transactions=total_transactions,
                               latest_block=latest_block,
                               plot_url=analytics_data['plots'],
                               stats=analytics_data['stats'],
                               chain=chain)
    return redirect(url_for('login'))

@app.route('/register_product', methods=['GET', 'POST'])
def register_product():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_batch_id = request.form['product_batch_id']
        product_name = request.form['product_name']
        quantity = request.form['quantity']
        product_owner = request.form['product_owner']
        timestamp = request.form['timestamp']
        storage_temperature = request.form['storage_temperature']
        humidity = request.form['humidity']
        location = request.form['location']
        
        user_email = session['email']
        user = users.get(user_email)
        
        if user:
            sender = user['public_key']
            
            # Mine a new block to include the new product transaction
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)
            
            blockchain.new_transaction(
                sender=sender,
                recipient=product_owner,
                product_id=product_batch_id,
                product_name=product_name,
                quantity=quantity,
                timestamp=timestamp,
                storage_temperature=storage_temperature,
                humidity=humidity,
                location=location
            )
            
            previous_hash = blockchain.hash(last_block)
            blockchain.new_block(proof, previous_hash)
            
            flash('Product details saved successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('User not found!', 'danger')
            return redirect(url_for('login'))
    
    products = []
    for block in blockchain.chain:
        for tx in block['transactions']:
            if tx['sender'] == '0': # Registered products
                products.append(tx)
            
    return render_template('product.html', role=session['role'], products=products)

@app.route('/product_history', methods=['GET', 'POST'])
def product_history():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form['product_id']
        product_history = []
        for block in blockchain.chain:
            for tx in block['transactions']:
                if tx['product_id'] == product_id:
                    product_history.append(tx)
        return render_template('product_history.html', role=session['role'], product_history=product_history, product_id=product_id)

    return render_template('product_history.html', role=session['role'])

@app.route('/track_product', methods=['GET', 'POST'])
def track_product():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form['product_id']
        product_history = []
        for block in blockchain.chain:
            for tx in block['transactions']:
                if tx['product_id'] == product_id:
                    product_history.append(tx)
        return render_template('track_product.html', role=session['role'], product_history=product_history, product_id=product_id)

    return render_template('track_product.html', role=session['role'])

@app.route('/transfer_ownership', methods=['GET', 'POST'])
def transfer_ownership():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_id = request.form['product_id']
        new_owner = request.form['new_owner']
        
        user_email = session['email']
        user = users.get(user_email)
        
        if user:
            sender = user['public_key']
            
            # Find the latest transaction for the product
            latest_transaction = None
            for block in reversed(blockchain.chain):
                for tx in reversed(block['transactions']):
                    if tx['product_id'] == product_id:
                        latest_transaction = tx
                        break
                if latest_transaction:
                    break
            
            if latest_transaction and latest_transaction['recipient'] == sender:
                last_block = blockchain.last_block
                last_proof = last_block['proof']
                proof = blockchain.proof_of_work(last_proof)
                
                blockchain.new_transaction(
                    sender=sender,
                    recipient=new_owner,
                    product_id=product_id,
                    product_name=latest_transaction['product_name'],
                    quantity=latest_transaction['quantity'],
                    timestamp=latest_transaction['timestamp'],
                    storage_temperature=latest_transaction['storage_temperature'],
                    humidity=latest_transaction['humidity'],
                    location=latest_transaction['location']
                )
                
                previous_hash = blockchain.hash(last_block)
                blockchain.new_block(proof, previous_hash)
                
                flash('Ownership transferred successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('You do not own this product or product does not exist!', 'danger')
                return redirect(url_for('transfer_ownership'))
        else:
            flash('User not found!', 'danger')
            return redirect(url_for('login'))
            
    return render_template('transfer_ownership.html', role=session['role'])

@app.route('/analytics')
def analytics_page():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    chain = blockchain.chain
    analytics_data = generate_plots(chain)
    
    return render_template('analytics.html',
                           role=session['role'],
                           plot_url=analytics_data['plots'],
                           stats=analytics_data['stats'])

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        product_id="0",
        product_name="Mined Coin",
        quantity=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'product_id', 'product_name', 'quantity']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['product_id'], values['product_name'], values['quantity'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
