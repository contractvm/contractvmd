# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import imp
import sys

from .database import Database
from . import config

logger = logging.getLogger(config.APP_NAME)


class PluginManager:
	def __init__ (self):
		self.dapps = {}

	def load (self, pname, chain, db, dht, api):
		logger.pluginfo ('Plugging dapp "%s"', pname.lower ())

		dapp = imp.load_source (pname, config.DATA_DIR + '/dapps/' + pname + '/dapp/__init__.py')
		pc = eval ('dapp.'+pname+'.'+pname)
		po = pc (chain, Database.new (config.DATA_DIR + '/dapps/state_' + pname + '_' + chain.getChainCode () + '.dat'), dht, api)

		# Register API methods
		rpcm = po.getAPI ().getRPCMethods ()
		for m in rpcm:
			api.registerRPCMethod (pname.lower () + '.' + m, rpcm[m])

		self.dapps[pname.lower ()] = po


	# Return true if the message should be handled
	def shouldBeHandled (self, m):
		for p in self.dapps:
			if m.DappCode == self.dapps[p].DappCode:
				return True
		return False

	# Handle message received from the DHT
	def handleMessage (self, m):
		for p in self.dapps:
			if m.DappCode == self.dapps[p].DappCode:
				logger.pluginfo ('Found handler %s for message %s from %s', p, m.Hash, m.Player)
				try:					
					return self.dapps[p].handleMessage (m)
				except Exception as e:
					logger.critical ('Exception from dapp ' + p + ' while handling a message')
					logger.critical (e)
					return None

		logger.error ('Cannot handle message method %d for dapp %s', m.Method, str (m.DappCode))
		return None
