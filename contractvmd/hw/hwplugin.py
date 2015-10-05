# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, dapp
from ..proto import Protocol
from ..chain.message import Message

logger = logging.getLogger(config.APP_NAME)

class HelloWorldProto:
	DAPP_CODE = 0x05
	METHOD_HELLO = 0x01
	METHOD_LIST = [METHOD_HELLO]


class HelloWorldMessage (Message):
	def hello (name):
		m = HelloWorldMessage ()
		m.Name = name
		m.PluginCode = HelloWorldProto.DAPP_CODE
		m.Method = HelloWorldProto.METHOD_HELLO
		return m

	def toJSON (self):
		data = super (HelloWorldMessage, self).toJSON ()

		if self.Method == HelloWorldProto.METHOD_HELLO:
			data['name'] = self.Name
		else:
			return None

		return data



class HelloWorldAPI (dapp.API):
	def __init__ (self, vm, dht, api):
		self.api = api
		rpcmethods = {}

		rpcmethods["get_names"] = {
			"call": self.method_get_names,
			"help": {"args": [], "return": {}}
		}

		rpcmethods["hello"] = {
			"call": self.method_hello,
			"help": {"args": ["name"], "return": {}}
		}

		errors = {}

		super (HelloWorldAPI, self).__init__(vm, dht, rpcmethods, errors)
		#self.method_hello ('test')

	def method_get_names (self):
		return (self.vm.getNames ())

	def method_hello (self, name):
		message = HelloWorldMessage.hello (name)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		r = { "outscript": outscript, "datahash": datahash, "tempid": tempid, "fee": Protocol.estimateFee (self.vm.getChainCode (), 100 * len (name)) }
		return r


class HelloWorldCore (dapp.Core):
	def __init__ (self, chain, database):
		super (HelloWorldCore, self).__init__ (chain, database)
		self.database.init ('names', {})

	def addName (self, name):
		name = name.lower ()
		names = self.database.get ('names')
		if name in names:
			names[name] += 1
		else:
			names[name] = 1
		self.database.set ('names', names)

	def getNames (self):
		return self.database.get ('names')
	

class HelloWorldDapp (dapp.Dapp):
	def __init__ (self, chain, db, dht, apimaster):
		self.core = HelloWorldCore (chain, db)
		api = HelloWorldAPI (self.core, dht, apimaster)
		super (HelloWorldDapp, self).__init__("HW", HelloWorldProto.DAPP_CODE, HelloWorldProto.METHOD_LIST, chain, db, dht, api)

	def handleMessage (self, m):
		if m.Method == HelloWorldProto.METHOD_HELLO:
			logger.pluginfo ('Found new message %s: hello %s', m.Hash, m.Data['name'])
			self.core.addName (m.Data['name'])
			
		
