# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from ..message import Message
from .proto import EthProto

class EthMessage (Message):
	def contract (contract_code, player):
		m = EthMessage ()
		m.Player = player
		m.ContractCode = contract_code
		m.Method = EthProto.METHOD_CONTRACT
		m.PluginCode = EthProto.PLUGIN_CODE
		return m

	def send (contract, values, player):
		m = EthMessage ()
		m.Player = player
		m.Contract = contract
		m.Values = values
		m.Method = EthProto.METHOD_SEND
		m.PluginCode = EthProto.PLUGIN_CODE
		return m

	def toJSON (self):
		data = super (EthMessage, self).toJSON ()

		if self.Method == TSTProto.METHOD_CONTRACT:
			data['contract_code'] = self.ContractCode
		elif self.Method == TSTProto.METHOD_SEND:
			data['contract'] = self.Contract
			data['values'] = self.Values
		else:
			return None

		return data
