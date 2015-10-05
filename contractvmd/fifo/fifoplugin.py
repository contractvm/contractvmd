# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, dapp
from ..proto import Protocol
from ..chain.message import Message

logger = logging.getLogger(config.APP_NAME)

class FIFOProto:
	DAPP_CODE = 0x09
	METHOD_PUBLISH_MESSAGE = 0x01
	METHOD_LIST = [METHOD_PUBLISH_MESSAGE]


class FIFOMessage (Message):
	def publishMessage (queue, body):
		m = FIFOMessage ()
		m.Queue = queue
		m.Body = body
		m.PluginCode = FIFOProto.DAPP_CODE
		m.Method = FIFOProto.METHOD_PUBLISH_MESSAGE
		return m

	def toJSON (self):
		data = super (FIFOMessage, self).toJSON ()

		if self.Method == FIFOProto.METHOD_PUBLISH_MESSAGE:
			data['queue'] = self.Queue
			data['body'] = self.Body
		else:
			return None

		return data


class FIFOAPI (dapp.API):
	def __init__ (self, vm, dht, api):
		self.api = api
		rpcmethods = {}

		rpcmethods["publish_message"] = {
			"call": self.method_publish_message,
			"help": {"args": ["queue", "body"], "return": {}}
		}

		rpcmethods["get_messages"] = {
			"call": self.method_get_messages,
			"help": {"args": ["queue", "last"], "return": {}}
		}

		errors = {}

		super (FIFOAPI, self).__init__(vm, dht, rpcmethods, errors)


	def method_publish_message (self, queue, body):
		message = FIFOMessage.publishMessage (queue, body)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		r = { "outscript": outscript, "datahash": datahash, "tempid": tempid, "fee": Protocol.estimateFee (self.vm.getChainCode (), 100 * len (body)) }
		return r
		
	def method_get_messages (self, queue, last):
		return self.vm.getMessages (queue, last)

class FIFOCore (dapp.Core):
	def __init__ (self, chain, database):
		super (FIFOCore, self).__init__ (chain, database)

	def publishMessage (self, queue, body):
		qlist = []
		if self.database.exists (queue):
			qlist = self.database.get (queue)
		else:
			qlist = []
		qlist.append (body)
		self.database.set (queue, qlist)
		return True

	def getMessages (self, queue, last):
		try:
			msgs = self.database.get (queue)
			msgsn = msgs[int (last):]
		except:
			msgs = []
			msgsn = []
		return {'size': len (msgs), 'messages': msgsn}
	

class FIFODapp (dapp.Dapp):
	def __init__ (self, chain, db, dht, apimaster):
		self.core = FIFOCore (chain, db)
		api = FIFOAPI (self.core, dht, apimaster)		
		super (FIFODapp, self).__init__("FIFO", FIFOProto.DAPP_CODE, FIFOProto.METHOD_LIST, chain, db, dht, api)
		

	def handleMessage (self, m):
		if m.Method == FIFOProto.METHOD_PUBLISH_MESSAGE:
			logger.pluginfo ('Found new message %s: publish on queue %s', m.Hash, m.Data['queue'])
			self.core.publishMessage (m.Data['queue'], m.Data['body'])
			
		
