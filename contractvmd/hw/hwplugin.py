# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, plugin
from ..proto import Protocol
from ..chain.message import Message

logger = logging.getLogger(config.APP_NAME)

class HelloWorldProto:
	PLUGIN_CODE = 0x05
	METHOD_HELLO = 0x01
	METHOD_LIST = [METHOD_HELLO]


class HelloWorldMessage (Message):
	def hello (name):
		m = HelloWorldMessage ()
		m.Name = name
		m.PluginCode = HelloWorldProto.PLUGIN_CODE
		m.Method = HelloWorldProto.METHOD_HELLO
		return m

	def toJSON (self):
		data = super (HelloWorldMessage, self).toJSON ()

		if self.Method == HelloWorldProto.METHOD_HELLO:
			data['name'] = self.Name
		else:
			return None

		return data



class HelloWorldAPI (plugin.API):
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


class HelloWorldVM (plugin.VM):
	def __init__ (self, chain, database):
		super (HelloWorldVM, self).__init__ (chain, database)
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
	

class HelloWorldPlugin (plugin.Plugin):
	def __init__ (self, chain, db, dht, apimaster):
		self.VM = HelloWorldVM (chain, db)
		super (HelloWorldPlugin, self).__init__("HW", HelloWorldProto.PLUGIN_CODE, HelloWorldProto.METHOD_LIST, chain, db, dht)
		self.API = HelloWorldAPI (self.VM, self.DHT, apimaster)

	def getAPI (self):
		return self.API

	def handleMessage (self, m):
		if m.Method == HelloWorldProto.METHOD_HELLO:
			logger.pluginfo ('Found new message %s: hello %s', m.Hash, m.Data['name'])
			self.VM.addName (m.Data['name'])
			
		
