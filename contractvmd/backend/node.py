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
from protocoin import clients, networks, node
from ..chain.message import Message

from .backend import *
from .. import config

logger = logging.getLogger(config.APP_NAME)


class Node (Backend):
	# TODO must check if the block contains any block with OPRETURN and magiccode.
	# Return a block with transactions that contains only the magicode
	# chain.isMessage check a single transaction
	def blockFilter (block):
		v = []
		for tx in txns:
			if Message.isMessage (tx):
				v.append (tx)

		if len (v) == 0:
			return None

		block.txns = v
		return block

	def __init__ (self, chain, dbfile, genesisblock = None):
		if not networks.isSupported (chain):
		    raise ChainNotSupportedException ()

		self.genesis = genesisblock
		self.tx_cache = {}
		self.thread = None
		self.node = node.ProtocoinNode (chain, dbfile, self.genesis[0], self.genesis[1])
		self.node.blockFilter = Node.blockFilter

	def getChainCode (self):
		return self.chain

	def connect (self):
		logger.info ('Waiting for bootstrap from seed servers')
		try:
			self.node.bootstrap ()
		except:
			logger.critical ('No reachable seed server found')
			return False

		try:
			self.node.connect ()
		except:
			logger.critical ('No peer available')

		self.thread = Thread (target=self.node.loop, args=())
		self.thread.start ()
		return True

	def getLastBlockHeight (self):
		return self.node.getLastBlockHeight ()

	def getBlockHash (self, index):
		return self.node.getBlockHash (index)

	def getBlockByHash (self, bhash):
		b = self.node.getBlockByHash (bhash)
		self.tx_cache = b.txns
		block = {"height": '', "time": '', "hash": bhash, "tx": d['data']['txs']}
		return block

	def broadcastTransaction (self, transaction):
		return self.node.broadcastTransaction (transaction)

	def getTransaction (self, txid):
		return self.tx_cache [txid]
