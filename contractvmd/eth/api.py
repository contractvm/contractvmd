import copy

from .. import plugin
from ..proto import Protocol

class EthAPI (plugin.API):	
	def __init__ (self, vm, dht):
		errors = {}
		rpcmethods = {}

		rpcmethods["contract"] = {'call': self.method_contract, 'help': {"args": ["contract_code", "player_address"], 
			"return": {"outscript": "", "datahash": "", "fee": ""}}}
		rpcmethods["info"] = {'call': self.method_info, 'help': {}, "return": {}}

		super (EthAPI, self).__init__(vm, dht, rpcmethods, errors)

		#self.method_tell ('<contract><intaction id="test" /></contract>', 'mn1FwcHcUDodajXGUFRdzx23BpGU7GJ7DV', 100)


	def method_contract (self, contract_code, player):
		pass

 
	# Return tstvm informations
	def method_info (self):
		return (self.vm.getChainState ())
		

