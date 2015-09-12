# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import requests
import json

from .backend import Backend

class ChainSoAPI (Backend):
	SUPPORTED_CHAINS = ['BTC', 'XTN', 'DOGE', 'XDT', 'LTC', 'XLT']

	def __init__ (self, chain):
		self.chain = chain

		if self.chain == 'BTC':
			self.chainstr = 'BTC'
		elif self.chain == 'XTN':
			self.chainstr = 'BTCTEST'
		elif self.chain == 'DOGE':
			self.chainstr = 'DOGE'
		elif self.chain == 'XDT':
			self.chainstr = 'DOGETEST'
		elif self.chain == 'LTC':
			self.chainstr = 'LTC'
		elif self.chain == 'XLT':
			self.chainstr = 'LTCTEST'
		else:
			#TODO fatal error
			pass

	def getSupportedChains ():
		return ChainSoAPI.SUPPORTED_CHAINS

	def isChainSupported (chain):
		return chain in ChainSoAPI.SUPPORTED_CHAINS

	def getJsonFromUrl (self, u):
		r = requests.get(u)
		return json.loads (r.text)

	def connect (self):
		pass


	def getLastBlockHeight (self):
		u = 'https://chain.so/api/v2/get_info/' + self.chainstr
		d = self.getJsonFromUrl (u)
		return int (d['data']['blocks'])


	def getBlockHash (self, index):
		u = 'https://chain.so/api/v2/get_blockhash/'+self.chainstr+'/' + str (index)
		d = self.getJsonFromUrl (u)
		return str (d['data']['blockhash'])
	

	def getBlockByHash (self, bhash):
		u = 'https://chain.so/api/v2/get_block/'+self.chainstr+'/' + str (bhash)
		d = self.getJsonFromUrl (u)
		block = {"height": d['data']['block_no'], "time": d['data']['time'], "hash": d['data']['blockhash'], "tx": d['data']['txs']}
		return block


	def getTransaction (self, txid):
		d = None
		try:
			u = 'https://chain.so/api/v2/get_tx/'+self.chainstr+'/' + str (txid)
			d = self.getJsonFromUrl (u)
			return d['data']['tx_hex']
		except:
			print (u,d)

	def broadcastTransaction (self, transaction):
		raise ('This is an abstract method')


		
