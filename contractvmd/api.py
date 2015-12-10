# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import time
import logging
import json
import inspect
import random

from . import config
from .proto import Protocol
from .chain.message import *

from threading import Thread
from threading import Lock
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher


logger = logging.getLogger(config.APP_NAME)
logging.getLogger('werkzeug').setLevel(logging.ERROR)



class API:
	def __init__ (self, backend, chain, dht, port, threads):
		self.port = int (port)
		self.threads = int (threads)

		self.dht = dht
		self.backend = backend
		self.chain = chain

		self.RPCHelp = {
			"broadcast" : {"args": ["signed_transaction", "temp_id"], "return": {'txid': 'transaction_hash'}},
			"info" : {"args": [], "return": {
			    "chain": {
				"code": "XLT",
				"height": 561596,
				"name": "Litecoin testnet"
			    },
			    "node": {
				"backend": [ "rpc", "chainsoapi" ],
				"dapps": { "list": [ "cotst" ], "enabled": [ "cotst" ] },
				"version": "0.1"
			    }
			}},
			"net.peers": {"args": [], "return": {"list": [("host", "port", "id")]}},
			"net.connections": {"args": [], "return": {"count": 'total_peers'}},
			"help": {"args":[], "return": {}}
		}

		self.RPCDispatcher = {}
		self.RPCDispatcher["broadcast"] = self.method_broadcast
		self.RPCDispatcher["help"] = self.method_help
		self.RPCDispatcher["info"] = self.method_info
		self.RPCDispatcher["net.peers"] = self.method_net_peers
		self.RPCDispatcher["net.connections"] = self.method_net_connections


	def registerRPCMethod (self, name, method):
		self.RPCDispatcher [name] = method['call']
		self.RPCHelp [name] = method['help']


	def method_net_connections (self):
		return {'count': len (self.dht.peers ())}

	def method_net_peers (self):
		return self.dht.peers ()


	# Broadcast a signed transaction
	def method_broadcast (self, thex, temp_id):
		# TODO check if temp_id is associated with the player who signed thex

		# Check the validity of the signed transaction

		# Use the backend to broadcast the transaction and get txid
		r = self.backend.broadcastTransaction (thex)

		# Publish the temp data on the DHT
		if r != None:
			self.dht.publish (temp_id, r)

		# Return the transaction id to the client
		return {'txid': r}


	def method_help (self):
		return self.RPCHelp


	def method_info (self):
		return {'chain': {'height': self.chain.getChainHeight (), 'regtest': config.CONF['regtest'],
			'code': self.chain.getChainCode (), 'name': self.chain.getChainName ()},
			'node': { 'dapps': config.CONF['dapps'], 'backend': config.CONF['backend']['protocol'],
			'version': config.APP_VERSION }}



	@Request.application
	def serveApplication (self, request):
		try:
			rjson = json.loads (request.data.decode('ascii'))
		except:
			apiresponse = Response({}, mimetype='application/json')
			apiresponse.headers.add('Access-Control-Allow-Origin', '*')
			apiresponse.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
			apiresponse.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
			return apiresponse

		if rjson['method'] in self.RPCDispatcher:
			nargs = len (inspect.getargspec (self.RPCDispatcher[rjson['method']]).args) - 1

			if len (rjson['params']) != nargs:
				logger.error ('Client invalid request arguments: "%s" %s', rjson['method'], str(rjson['params']))
			else:
				if rjson['method'].find ('get') == -1 and rjson['method'].find ('info') == -1:
					logger.debug ('Client request: %s', rjson['method'])
		else:
			logger.error ('Client invalid request: "%s" %s', rjson['method'], str(rjson['params']))

		response = JSONRPCResponseManager.handle (request.data, self.RPCDispatcher)
		apiresponse = Response(response.json, mimetype='application/json')
		apiresponse.headers.add('Access-Control-Allow-Origin', '*')
		apiresponse.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
		apiresponse.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
		return apiresponse

	def serverThread (self):
		if self.threads > 1:
			run_simple('localhost', self.port, self.serveApplication, threaded=True, processes=self.threads, use_debugger=False)
		else:
			run_simple('localhost', self.port, self.serveApplication, use_debugger=False)


	def run (self):
		logger.info ('Starting jsonrpc api server at port %d (%d threads)', self.port, self.threads)

		# Start the serve thread
		self.servethread = Thread(target=self.serverThread, args=())
		self.servethread.start()
