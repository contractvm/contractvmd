# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import time
import logging
import random
import kad
import threading
from threading import Thread, Lock, Timer

from . import config

logger = logging.getLogger(config.APP_NAME)

class DHT:
	def __init__ (self, port, seedlist = [], dhtfile = '', info = {}):
		self.dhtfile = dhtfile
		self.seeds = []
		self.info = info
		self.port = port
		self.temp = {'index': 0}
		self.storage = kad.storage.Shelve (self.dhtfile)
		self.writelock = Lock ()

		##TODO Open the peers file and search for seed peers
		
		for peer in seedlist:
			peer = peer.split (':')

			if len (peer) == 2:
				self.seeds.append ((peer[0], int (peer[1])))
				logger.debug ('Binding peer (%s:%d)', peer[0], int (peer[1]))
			#else:
			#	self.seeds.append ((peer[0], port))
			#	logger.debug ('Binding peer (%s:%d)', peer[0], port)


	# Temp data
	def prepare (self, data):
		self.writelock.acquire ()
		self.temp ['index'] += 1
		tempid = str (self.temp['index'])
		self.temp [tempid] = data
		logger.debug ('Prepare temp data %s (%d in the buffer)', str (tempid), len (self.temp))
		self.writelock.release ()
		return tempid


	def publish (self, tempid, key):
		self.writelock.acquire ()
		tempid = str (tempid)
		if not tempid in self.temp:
			self.writelock.release ()
			return None

		logger.debug ('Publish temp data %s -> %s', str (tempid), key)
		data = self.temp[tempid]
		r = self.set (key, data)
		del self.temp[str (tempid)]
		self.writelock.release ()
		return r

	def startServiceThread (self):
		self.thread = Thread(target=self.serviceThread, args=())
		self.thread.start()

	def run (self):
		logger.info ('Bootstraping DHT from %d nodes, listening on port %d', len (self.seeds), self.port)
		self.bootstrap ()


	def set (self, key, value):
		#self.storage.dump ()

		#try:
		self.dht [key] = value
		logger.debug ("Storing %s", key)
		return True
		#except:
		#	logger.error ('Error while setting data in the dht')
		#	return False


	def identity (self):
		return self.dht.identity ()
		
	def get (self, key, handler, handlerdata):
		#self.storage.dump ()
		logger.info ('Waiting for %s', key)
		self.dht.get (key, lambda d: handler (handlerdata, d))

	def bootstrap (self):
		self.dht = kad.DHT ('', int (self.port), storage=self.storage, info=str (self.info))
		self.dht.bootstrap (self.seeds)
		self.startServiceThread ()



	def peers (self):
		return self.dht.peers ()

	def serviceThread (self):
		i = 0
		while True:
			if i % 4 == 0:
				logger.debug ('Discovering nodes, %d total', len (self.peers ()))
			try:
				self.dht.bootstrap ()
			except:
				pass
			time.sleep (60)
			i += 1
