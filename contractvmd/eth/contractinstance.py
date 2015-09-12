# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config

logger = logging.getLogger(config.APP_NAME)

class ContractInstance:
	def __init__ (self, contract):
		self.contract = contract


	def send (self, data, player, time):
		pass


	def update (self, time):
		return self.contract
