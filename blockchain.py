
import json
from hashlib import sha256
import time
#from flask import Flask, request
#import requests



class  Block:

	#attribute hash is added at Blockhain methods

	def __init__(self, index, trans, time, prev_hash, nonce=0):
		self.index=index
		self.trans=trans
		self.time=time
		self.prev_hash=prev_hash
		self.nonce=nonce
		
	#@property
	def get_hash(self):
		json_data=json.dumps(self.__dict__,sort_keys=True)
		return sha256(json_data.encode()).hexdigest()

class Blockchain:

	difficulty=2

	def __init__(self):
		self.unconfirmed_trans=[]
		self.chain=[]
		self.create_gen()

	def create_gen(self):
		#creates first block in blockchain	
		gen=Block(0, [], time.time(), "0")
		gen.hash=gen.get_hash()
		self.chain.append(gen)

	@property
	def get_last(self):
		#gets the last block in chain
		return self.chain[-1]

	def proof_of_work(self, block):
		block.nonce=0
		computed=block.get_hash()
		while not computed.startswith("0" * Blockchain.difficulty):
			block.nonce+=1
			computed=block.get_hash()
		return computed

	def add_block(self, block, proof):
		#adds new block to the chain after verification

		#prev_hash=self.get_last.hash
		if self.get_last.hash != block.prev_hash:
			return False

		if not Blockchain.is_valid(block, proof):
			return False

		block.hash=proof
		self.chain.append(block)
		return True

	@classmethod
	def is_valid(cls, block, block_hash):
		#checks if hash is valid and difficult enough
		return (block_hash.startswith('0' * Blockchain.difficulty) and 
			block_hash == block.get_hash())

	def add_new_trans(self, trans):
		self.unconfirmed_trans.append(trans)

	def mine(self):
		#interface of adding pending transactions to the blockchain
		if not self.unconfirmed_trans:
			return False
		last_block = self.get_last
		new_block = Block(index = last_block.index + 1,
						  trans = self.unconfirmed_trans,
						  time = time.time(),
						  prev_hash = last_block.hash)

		proof = self.proof_of_work(new_block)
		self.add_block(new_block, proof)

		self.unconfirmed_trans = []
		announce_new_block(new_block)
		return new_block.index

	@classmethod
	def check_chain(cls, chain):
		result = True
		prev_hash = "0"

		for block in chain:
			block_hash = block.hash
			delattr(block, "hash")

			if not cls.is_valid(block, block.hash) or \
					prev_hash != block.prev_hash:
				result = False
				break

			block.hash, prev_hash = block_hash, block_hash

		return result

	

from backend import announce_new_block
