# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import requests
import json
import logging
import time
import shelve
import socket
import codecs
from threading import Thread
from threading import Lock
from protocoin import clients, networks
from protocoin.clients import *

from .backend import *
from .. import config

logger = logging.getLogger(config.APP_NAME)



class ProtocoinClient (clients.ChainClient):
	def __init__ (self, chaincode, dbf, genesis):
		self.genesis = genesis
		self.dbfile = dbf
		self.connlock = Lock ()
		self.db = shelve.open (self.dbfile)

		self.sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(('localhost', 19333)) #networks.peers[chaincode][0])

		self.db['txcache'] = {}
			
		if 'current' in self.db:
			self.current = self.db['current']
		else:
			self.current = genesis
			self.db['current'] = genesis
			
		super (ProtocoinClient, self).__init__ (self.sock, chaincode)

	def chainloop (self):
		while True:
			try:
				self.loop ()
			except:
				self.connlock.acquire ()
				logger.critical ('Disconnected from peers, reconnecting...')
				try:
					self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self.sock.connect(('localhost', 19333)) #networks.peers[chaincode][0])
					self.update_socket (self.sock)
					logger.debug ('Connection enstablished')
				except:
					pass
				self.connlock.release ()
			
		
	def sync (self):
		while True:
			self.connlock.acquire ()
			#logger.debug ('Last block is %s at height %d', hex (int (self.current[0], 16)), self.current[1])
			getblock = GetBlocks ([int (self.current[0], 16)])
			self.send_message (getblock)
			self.connlock.release ()
			time.sleep (10)

	def close (self):
		self.sock.close ()

	def handle_block(self, message_header, message):
		print (message)
		print ("Block hash:", message.calculate_hash())

		if message.prev_block == int (self.current[0], 16):
			bl = { 'height': self.current[1] + 1, 'hash': str (message.calculate_hash ())[2:-1], 'tx': [], 'txs': {}, 'time': message.timestamp}

			for tx in message.txns:
				print (tx)
				txid = str (tx.calculate_hash ())[2:-1]
				bl['tx'].append (txid)
				hash_fields = ["version", "tx_in", "tx_out", "lock_time"]
				serializer = TxSerializer()
				bin_data = serializer.serialize(tx, hash_fields)
				bl['txs'][txid] = codecs.encode (bin_data, 'hex')
			print (bl)

			self.db['txcache'] = bl['txs']
			self.db[bl['hash']] = bl
			self.db[str(bl['height'])] = bl['hash']
			self.current = (bl['hash'], bl['height'])
			self.db['current'] = self.current
			
			
	def handle_inv(self, message_header, message):
		#print (message_header)
		getdata = GetData()
		getdata_serial = GetDataSerializer ()
		getdata.inventory = message.inventory
		self.send_message (getdata)


	def getLastBlockHeight (self):
		return self.current [1]

	def getBlockHash (self, index):
		return self.db [str (index)]

	def getBlockByHash (self, bhash):
		return self.db [bhash]

	def broadcastTransaction (self, transaction):
		return None

	def getTransaction (self, txid):
		return self.db['txcache'][txid]


class Node (Backend):
	def __init__ (self, chain, dbfile, genesisblock = None):
		if not networks.isSupported (chain):
		    raise ChainNotSupportedException ()

		self.chain = chain
		self.client = None
		self.loopthread = None
		self.syncthread = None
		self.dbfile = dbfile
		self.genesis = genesisblock
		
	def getChainCode (self):
		return self.chain

	def connect (self):
		if self.client != None:
			return
		#	self.client.close ()
			
		if self.syncthread != None:
			pass # kill the old thread, if any
		
		try:
			self.client = ProtocoinClient (self.chain, self.dbfile, self.genesis)
		except:
			return False
		
		self.client.handshake()

		self.syncthread = Thread(target=self.client.sync, args=())
		self.syncthread.start()

		self.loopthread = Thread(target=self.client.chainloop, args=())
		self.loopthread.start()

		return True

	def getLastBlockHeight (self):
		return self.client.getLastBlockHeight ()

	def getBlockHash (self, index):
		return self.client.getBlockHash (index)

	def getBlockByHash (self, bhash):
		return self.client.getBlockByHash (bhash)

	def broadcastTransaction (self, transaction):
		return None

	def getTransaction (self, txid):
		return None

