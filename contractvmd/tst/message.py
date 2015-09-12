# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from ..chain.message import Message
from .proto import TSTProto

class TSTMessage (Message):
	def tell (contract, player, expire = 100):
		m = TSTMessage ()
		m.Player = player
		m.Contract = contract
		m.Method = TSTProto.METHOD_TELL
		m.PluginCode = TSTProto.PLUGIN_CODE
		m.Expire = int (expire)
		return m

	def do (session, action, value, nonce, player):
		m = TSTMessage ()
		m.Player = player
		m.Action = action
		m.Session = session
		m.Value = value
		m.Nonce = nonce
		m.Method = TSTProto.METHOD_DO
		m.PluginCode = TSTProto.PLUGIN_CODE
		return m

	def fuse (contractp, contractq, player):
		m = TSTMessage ()
		m.Player = player
		m.ContractP = contractp
		m.ContractQ = contractq
		m.Method = TSTProto.METHOD_FUSE
		m.PluginCode = TSTProto.PLUGIN_CODE
		return m


	def fuse_net (contractp, contractq, node):
		m = TSTMessage ()
		m.Player = node
		m.ContractP = contractp
		m.ContractQ = contractq
		m.Method = TSTProto.METHOD_FUSE_NET
		m.PluginCode = TSTProto.PLUGIN_CODE
		return m

	def accept (contract, player):
		m = TSTMessage ()
		m.AcceptedContract = contract
		m.Player = player
		m.Method = TSTProto.METHOD_ACCEPT
		m.PluginCode = TSTProto.PLUGIN_CODE
		return m

	def toJSON (self):
		data = super (TSTMessage, self).toJSON ()

		if self.Method == TSTProto.METHOD_TELL:
			data['contract'] = self.Contract
			data['expire'] = self.Expire
		elif self.Method == TSTProto.METHOD_DO:
			data['action'] = self.Action
			data['sessionhash'] = self.Session
			data['value'] = self.Value
			data['nonce'] = str (self.Nonce)	
		elif self.Method == TSTProto.METHOD_FUSE or self.Method == TSTProto.METHOD_FUSE_NET:
			data['contractphash'] = self.ContractP
			data['contractqhash'] = self.ContractQ
		elif self.Method == TSTProto.METHOD_ACCEPT:
			data['contracthash'] = self.AcceptedContract
		else:
			return None

		return data
