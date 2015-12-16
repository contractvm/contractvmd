# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import datetime
import time
import logging
import copy
from threading import Thread
from threading import Lock

from .. import config
from .blockwatch import *
from .message import *

logger = logging.getLogger(config.APP_NAME)


class Chain:
	DATA_TIMEOUT = 15
	DATA_HANDLER_TIMEOUT = 5

	def __init__ (self, plugman, database, backend, dht, chain):
		self.plugman = plugman
		self.backend = backend
		self.database = database
		self.chainHeight = int (self.database.getinit ('ChainHeight', 0))
		self.chain = chain
		self.queue = []
		self.queuelock = Lock ()
		self.dht = dht
		self.dhtrequests = {}
		self.dhtqueue = []
		self.dhtdatalock = Lock ()

	def getChainName (self):
		return self.chain['name']

	def getChainCode (self):
		return self.chain['code']

	def getChainHeight (self):
		return int (self.chainHeight)

	def updateChainHeight (self, h):
		self.chainHeight = int (h)
		self.database.set ('ChainHeight', int (h))

	def newBlockHandler (self, i):
		logger.info ('New block found %d', i)

		# Insert the block into a queue
		self.queuelock.acquire ()
		self.queue.append (i)
		self.queuelock.release ()


	def onMessageDataReceived (self, message, data):
		if data == None:
			logger.error ('Cannot retrive data %s from DHT', message.Hash)
			return

		# Check hash validity
		if message.getDataHash (data) != message.DataHash:
			logger.error ('Invalid data hash (%s <> %s', message.getDataHash (data), message.DataHash)
			#return

		message.Data = json.loads (data)


		# Check data <=> metadata consistency
		#if message.Data['player'] != message.Player:
		#	logger.error ('Different players between transaction and data (%s <> %s)', message.Data['player'], message.Player)
		#	#return

		if int (message.Data['method']) != int (message.Method):
			logger.error ('Different method between transaction and data')
			#return

		self.dhtdatalock.acquire ()
		# dhtrequests doesn't contain message.Block if the timer for data is expired
		if message.Block in self.dhtrequests:
			self.dhtrequests [message.Block]['list'][message.Hash] = message
			self.dhtrequests [message.Block]['pending'] -= 1
			#print (message.Block, self.dhtrequests [message.Block]['pending'], message.Hash)
		self.dhtdatalock.release ()

		#self.plugman.handleMessage (message)


	def parseBlock (self, blockn):
		block = self.backend.getBlock (blockn)

		if block == None:
			logger.debug ('Waiting for block...')
			time.sleep (2)
			return
		
		logger.debug ('Parsing block %s - %d %s',
			datetime.datetime.fromtimestamp(int(block['time'])).strftime('%Y-%m-%d %H:%M:%S'),
			block['height'], block['hash'])

		for txid in block['tx']:
			txhex = self.backend.getTransaction (txid)

			if txhex != None:
				#logger.debug ('Parsing transaction %s of block %d', txid, nblock)


				if True: #try:
					message = Message.fromTransaction (block['height'], txhex)

					if message != None:
						if self.plugman.shouldBeHandled (message):
							self.dhtdatalock.acquire ()
							if not message.Block in self.dhtrequests:
								self.dhtrequests[message.Block] = {'pending': 0, 'timer': 0, 'list': {}}

							self.dhtrequests [message.Block]['pending'] += 1
							self.dhtrequests [message.Block]['list'][message.Hash] = None

							if not message.Block in self.dhtqueue:
								self.dhtqueue.append (message.Block)

							self.dhtdatalock.release ()

							# Get data from DHT
							self.dht.get (message.Hash, self.onMessageDataReceived, message)
						else:
							logger.debug ('Message %s should not be handled, skipped', txid)

				#except:
				#	logger.error ('Failed to parse transaction %s of block %d', txid, nblock)
				#	continue

			else:
				logger.debug ('Cannot retrive transaction %s of block %d', txid, block['height'])

		# If the block is empty, we need to updateChainHeight
		self.dhtdatalock.acquire ()
		if len (self.dhtqueue) == 0:
			self.updateChainHeight (block['height'])
		self.dhtdatalock.release ()


	def dataHandler (self):
		while True:
			self.dhtdatalock.acquire ()

			if len (self.dhtqueue) > 0:
				logger.debug ("Data queue for block %d pending %d chunks with %d timer.", int (self.dhtqueue[0]),
					self.dhtrequests[self.dhtqueue[0]]['pending'],
					self.dhtrequests[self.dhtqueue[0]]['timer'])

			if len (self.dhtqueue) > 0 and (self.dhtrequests [self.dhtqueue[0]]['pending'] == 0 or
				self.dhtrequests [self.dhtqueue[0]]['timer'] > Chain.DATA_TIMEOUT):
					bn = self.dhtqueue.pop (0)

					logger.debug ('Data of block %d retrived',bn)

					mhashs = self.dhtrequests[bn]['list']

					for m in mhashs:
						mdata = self.dhtrequests[bn]['list'][m]

						if mdata != None:
							self.plugman.handleMessage (mdata)
						else:
							logger.error ("Skipping message %s due to a timeout", m)


					del self.dhtrequests[bn]
					self.dhtdatalock.release ()

					# Update here the chain height
					self.updateChainHeight (bn)


			elif len (self.dhtqueue) > 0 and self.dhtqueue[0] < self.dhtqueue[0] - 1:
				self.dhtdatalock.release ()
				self.updateChainHeight (self.dhtqueue[0]-1)

			else:
				for q in self.dhtqueue:
					self.dhtrequests [q]['timer'] += Chain.DATA_HANDLER_TIMEOUT

				self.dhtdatalock.release ()
				time.sleep (Chain.DATA_HANDLER_TIMEOUT)

	def run (self):
		# Start the blockwatch thread
		if self.getChainHeight () < self.chain['genesis_height']:
			cu = self.chain['genesis_height']
		else:
			cu = self.getChainHeight ()

		if config.CONF['discard-old-blocks']:
			logger.info ('Discarding old blocks')
			cu = self.backend.getLastBlockHeight () - 1

			# Update the chain height to avoid a full-sync in the next start
			self.updateChainHeight (self.backend.getLastBlockHeight () - 1)


		logger.info ('Starting chain loop from block %d on %s', cu, self.chain['name'])

		self.blockwatch = BlockWatch (cu, self.backend, self.newBlockHandler)
		self.blockwatchthread = Thread(target=self.blockwatch.run, args=())
		self.blockwatchthread.start()

		self.datawatchthread = Thread(target=self.dataHandler, args=())
		self.datawatchthread.start()

		while True:
			# Check for new queue elements
			self.queuelock.acquire ()
			if len (self.queue) > 0:
				nb = self.queue.pop (0)
			else:
				nb = None
			self.queuelock.release ()

			# Parse new data
			if nb != None:
				self.parseBlock (nb)


			time.sleep (0.1)
