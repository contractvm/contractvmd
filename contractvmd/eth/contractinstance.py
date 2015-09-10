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
