# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, plugin
from ..proto import Protocol

logger = logging.getLogger(config.APP_NAME)


# Virtual Machine
class EthCore (plugin.Core):
	def __init__ (self, chain, database):
		super (EthCore, self).__init__ (chain, database)
		self.database.init ('Contracts', [])


	def getStorageData (self, contracthash, data_index):
		return None


	def createContract (self, contracthash, contractcode, player, time):
		pass


	def send (self, contracthash, sendhash, data, player, time):
		pass


	def getSendResult (self, contracthash, sendhash):
		return None

	def getChainState (self):
		return {}
