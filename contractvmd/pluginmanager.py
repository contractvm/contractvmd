# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import imp
import sys
from colorlog import ColoredFormatter

from . import config

logger = logging.getLogger(config.APP_NAME)



class PluginManager:
	def __init__ (self):
		self.dapps = {}

	def load (self, pname, chain, db, dht, api):
		logger.pluginfo ('Plugging dapp "%s"', pname.lower ())

		#sys.path.append(config.DATA_DIR + '/dapps/'+pname+'/dapp/')
		dapp = imp.load_source (pname, config.DATA_DIR + '/dapps/'+pname+'/dapp/__init__.py') # + pname + '.py', open (config.DATA_DIR + '/dapps/'+pname+'/dapp/'+pname+'.py','r'))
		pc = eval ('dapp.'+pname+'.'+pname)

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
