# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, dapp
from ..proto import Protocol
from ..chain.message import Message

logger = logging.getLogger(config.APP_NAME)

class BlockStoreProto:
	DAPP_CODE = 0x08
	METHOD_SET = 0x01
	METHOD_LIST = [METHOD_SET]


class BlockStoreMessage (Message):
	def set (key, value):
		m = BlockStoreMessage ()
		m.Key = key
		m.Value = value
		m.DappCode = BlockStoreProto.DAPP_CODE
		m.Method = BlockStoreProto.METHOD_SET
		return m

	def toJSON (self):
		data = super (BlockStoreMessage, self).toJSON ()

		if self.Method == BlockStoreProto.METHOD_SET:
			data['key'] = self.Key
			data['value'] = self.Value
		else:
			return None

		return data


class BlockStoreAPI (dapp.API):
	def __init__ (self, core, dht, api):
		self.api = api
		rpcmethods = {}

		rpcmethods["get"] = {
			"call": self.method_get,
			"help": {"args": ["key"], "return": {}}
		}

		rpcmethods["set"] = {
			"call": self.method_set,
			"help": {"args": ["key", "value"], "return": {}}
		}

		errors = { 'KEY_ALREADY_SET': {'code': -2, 'message': 'Key already set'}, 'KEY_IS_NOT_SET': {'code': -3, 'message': 'Key is not set'} }


		super (BlockStoreAPI, self).__init__(core, dht, rpcmethods, errors)


	def method_get (self, key):
		v = self.core.get (key)
		if v == None:
			return self.createErrorResponse ('KEY_IS_NOT_SET')
		else:
			return v
		
	def method_set (self, key, value):
		if self.core.get (key) != None:
			return self.createErrorResponse ('KEY_ALREADY_SET')
		
		message = BlockStoreMessage.set (key, value)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		r = { "outscript": outscript, "datahash": datahash, "tempid": tempid, "fee": Protocol.estimateFee (self.core.getChainCode (), 100 * len (value)) }
		return r


class BlockStoreCore (dapp.Core):
	def __init__ (self, chain, database):
		super (BlockStoreCore, self).__init__ (chain, database)

	def set (self, key, value):
		if self.database.exists (key):
			return
		else:
			self.database.set (key, value)

	def get (self, key):
		if not self.database.exists (key):
			return None
		else:
			return self.database.get (key)
	

class BlockStoreDapp (dapp.Dapp):
	def __init__ (self, chain, db, dht, apiMaster):
		self.core = BlockStoreCore (chain, db)
		api = BlockStoreAPI (self.core, dht, apiMaster)
		super (BlockStoreDapp, self).__init__("BS", BlockStoreProto.DAPP_CODE, BlockStoreProto.METHOD_LIST, chain, db, dht, api)

	def handleMessage (self, m):
		if m.Method == BlockStoreProto.METHOD_SET:
			logger.pluginfo ('Found new message %s: set %s', m.Hash, m.Data['key'])
			self.core.set (m.Data['key'], m.Data['value'])
			
		
