# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
from colorlog import ColoredFormatter

from . import config

logger = logging.getLogger(config.APP_NAME)



class PluginManager:
	def __init__ (self):
		self.dapps = {}

	def load (self, pname, chain, db, dht, api):
		classname = config.DAPPS[pname.upper ()]

		logger.pluginfo ('Plugging dapp "%s"', pname.upper ())
		exec ('from .' + pname.lower() + '.' + pname.lower() + 'plugin import ' + classname + 'Dapp')
		pc = eval (classname+'Dapp')

		po = pc (chain, db.newNamespaceInstance (pname.upper () + '_'), dht, api)

		rpcm = po.getAPI ().getRPCMethods ()
		for m in rpcm:
			api.registerRPCMethod (pname.lower () + '.' + m, rpcm[m])

		self.dapps[po.Name] = po



	# Handle message received from the DHT
	def handleMessage (self, m):
		for p in self.dapps:
			if m.DappCode == self.dapps[p].DappCode:
				logger.pluginfo ('Found handler %s for message %s from %s', p, m.Hash, m.Player)
				return self.dapps[p].handleMessage (m)
		logger.error ('Cannot handle message method %d for dapp %d', m.Method, m.DappCode)
		return None
