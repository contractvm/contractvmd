# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import copy

from .. import plugin
from ..proto import Protocol

class EthAPI (plugin.API):	
	def __init__ (self, core, dht):
		errors = {}
		rpcmethods = {}

		rpcmethods["contract"] = {'call': self.method_contract, 'help': {"args": ["contract_code", "player_address"], 
			"return": {"outscript": "", "datahash": "", "fee": ""}}}
		rpcmethods["info"] = {'call': self.method_info, 'help': {}, "return": {}}

		super (EthAPI, self).__init__(core, dht, rpcmethods, errors)

		#self.method_tell ('<contract><intaction id="test" /></contract>', 'mn1FwcHcUDodajXGUFRdzx23BpGU7GJ7DV', 100)


	def method_contract (self, contract_code, player):
		pass

 
	# Return tstvm informations
	def method_info (self):
		return (self.core.getChainState ())
		

