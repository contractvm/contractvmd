# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, plugin
from . import core, api, proto

logger = logging.getLogger(config.APP_NAME)


class EthPlugin (plugin.Plugin):
	def __init__ (self, chain, db, dht):
		self.core = core.EthCore (chain, db)
		super (EthPlugin, self).__init__('ETH', proto.EthProto.PLUGIN_CODE, proto.EthProto.METHOD_LIST, chain, db, dht)
		self.API = api.EthAPI (self.core, self.DHT)


	def getAPI (self):
		return self.API

 
	def handleMessage (self, m):		
		logger.info ('Found new message: \'%s\' (proto: %d) (player: %s)', m.Method, 
					m.Protocol, m.Player)

		if m.Method == proto.EthProto.METHOD_CONTRACT:
			logger.info ('Found new message %s: contract')

			if not 'contract_code' in m.Data:
				return False
			else:
				m.ContractCode = m.Data['contract_code']
				#return self.VM.tell (m.Hash, m.Contract, m.Player, m.Expire, self.VM.getTime (m.Block))

		elif m.Method == proto.EthProto.METHOD_SEND:
			logger.info ('Found new message %s: send')

			if not 'contract' in m.Data or not 'values' in m.Data:
				return False
			else:
				m.Contract = m.Data['contract']
				m.Values = m.Data['values']
				#return self.VM.tell (m.Hash, m.Contract, m.Player, m.Expire, self.VM.getTime (m.Block))
