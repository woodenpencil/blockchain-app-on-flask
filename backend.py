"""
import json
#from hashlib import sha256
import time
import requests
"""
from blockchain import Blockchain, Block
from flask import Flask, request
app = Flask(__name__)

blockchain=Blockchain()

@app.route('/new_transaction', methods = ['POST'])
def new_trans():
	#endpoint to submit a new transaction

	tx_data = request.get_json()
	requered_flds = ["author", "content"]

	for field in requered_flds:
		if not tx_data.get(field):
			return "Invalid transaction data", 404

	tx_data["timestamp"] = time.time()

	blockchain.add_new_trans(tx_data)

	return "Succes", 201

@app.route('/chain', methods = ['GET'])
def get_chain():
	#returns the node's copy of the chain

	chain_data = []
	for block in blockchain.chain:
		chain_data.append(block.__dict__)
	return json.dumps({"length": len(chain_data),
					   "chain": chain_data,
					   "peers": list(peers)})

@app.route('/mine', methods = ['GET'])
def mine_unconfirmed_transactions():

	result = blockchain.mine()
	if not result:
		return "No transactions to mine"
	return "Block #{} is mined.".format(result)

@app.route('/get_tx')
def get_pending_tx():
	return json.dumps(blockchain.unconfirmed_trans)

peers = set()

@app.route('/register_node', methods = ['POST'])
def register_new_peers():
	node_address = request.get_json()["node_address"]
	if not node_address:
		return "Invalid data", 400

	#adds the node to the peer list
	peers.add(node_address)

	return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with():
	#registers current node with the node specified in the request

	node_address = request.get_json()["node_address"]
	if not node_address:
		return "Invalid data", 400

	data = {"node_address": request.host_url}
	headers = {'Content-Type': "application/json"}

	response = requests.post(node_address + "/register_node",
    						 data=json.dumps(data),
    						 headers=headers)

	if response.status_code == 200:
		global blockchain
		global peers

		chain_dump = response.json()['chain']
		blockchain = create_chain_from_dump(chain_dump)
		peers.update(response.json()['peers'])
		return "Registration succesful", 200
	else:
		return response.content, response.status_code

def create_chain_from_dump(chain_dump):
	gen_blockchain = Blockchain()
	gen_blockchain.create_gen()
	for idx, block_data in enumerate(chain_dump):
		if idx == 0:
			continue
		block = Block(block_data['index'], 
					  block_data['trans'], 
					  block_data['time'], 
					  block_data['prev_hash'],
					  block_data['nonce'])
		proof = block_data['hash']
		added = gen_blockchain.add_block(block, proof)
		if not added:
			raise Exception("The chain dump is tampered.")
	return gen_blockchain

def consensus():
    
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

def announce_new_block(block):
    
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["trans"],
                  block_data["time"],
                  block_data["prev_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201