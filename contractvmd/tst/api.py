# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import copy

from .. import dapp
from .message import TSTMessage
from .tibet import Tibet
from ..proto import Protocol

class TSTAPI (dapp.API):
	def __init__ (self, core, dht, api):
		self.api = api
		rpcmethods = {}
		rpcmethods["tell"] = {
			'call': self.method_tell,
			'help': {"args": ["contract_xml", "player_address", "expire_block_delta"],
			"return": {"outscript": "", "datahash": "", "fee": ""}}
		}

		rpcmethods["fuse"] = {
			'call': self.method_fuse,
			'help': {"args": ["contract1_hash", "contract2_hash", "player_address"],
			"return": {"outscript": "", "datahash": "", "fee": ""}}
		}

		rpcmethods["accept"] = {
			'call': self.method_accept,
			'help': {"args": ["contract_hash", "player_address"],
			"return": {"outscript": "", "datahash": "", "fee": ""}}
		}

		rpcmethods["broadcast_custom"] = {
			'call': self.method_broadcast_custom,
			'help': {"args": ["signed_transaction", "temp_id"],
				"return": {"txid": ""}}
		}
		rpcmethods["do"] = {
			'call': self.method_do,
			'help': {"args": ["session_hash", "action", "value", "nonce", "player_address"],
			"return": {"outscript": "", "datahash": "", "fee": ""}}
		}

		rpcmethods["listcontracts"] = {
			'call': self.method_listcontracts,
			'help': {"args": ["type=all|pending|fused|ended"],
			"return": [ {"type":"contract", "...": "..."}, {"type":"contract", "...":"..."} ]}
		}

		rpcmethods["listsessions"] = {
			'call': self.method_listsessions,
			'help': {"args": ["type=all|running|ended"],
                        "return": [ {"type":"session", "...": "..."}, {"type":"session", "...":"..."} ]}
		}

		rpcmethods["getcontract"] = {
			'call': self.method_getcontract,
			'help': {"args": ["contract_hash"],
			"return": {
			    "contract": "<contract><sequence><intaction id=\"a\"/><extaction id=\"b\"/></sequence></contract>",
			    "expiry": 100,
			    "hash": "f7163ae4cbd7790740000e45e7c1b9daeaadb7d88359d4e75756a417df59bce3",
			    "player": "mjBY56jFYRWXZEoYi8cztm7z8spjBht9iP",
			    "session": "ac35439702f82a17065ef6114dd07d8bccaa6fc3a9a99fed3e20f9cd92259352",
			    "time": 559992,
			    "type": "contract"
			}}
		}

		rpcmethods["compliantwithcontract"] = {
			'call': self.method_compliantwithcontract,
			'help': {"args": ["contract_hash"],
				"return": {
				    "contracts": [ "f7163ae4cbd7790740000e45e7c1b9daeaadb7d88359d4e75756a417df59bce3" ]
				}
			}
		}

		rpcmethods["getsession"] = {
			'call': self.method_getsession,
			'help': {"args": ["session_hash"],
			"return": {
			    "contracts": {
				"mjBY56jFYRWXZEoYi8cztm7z8spjBht9iP": "f7163ae4cbd7790740000e45e7c1b9daeaadb7d88359d4e75756a417df59bce3",
				"moRyzcLkAzN3kqwmFwMV2E5RLuK4SFCHyg": "211f823901753ffc7e2d361fa1d3b011102becd11a0a812be47cf0ab221205ee"
			    },
			    "hash": "ac35439702f82a17065ef6114dd07d8bccaa6fc3a9a99fed3e20f9cd92259352",
			    "players": {
				"mjBY56jFYRWXZEoYi8cztm7z8spjBht9iP": 0,
				"moRyzcLkAzN3kqwmFwMV2E5RLuK4SFCHyg": 1
			    },
			    "state": {
				"culpable": {
				    "0": False,
				    "1": False
				},
				"duty": {
				    "0": True,
				    "1": False
				},
				"end": False,
				"history": { 1: '6d9ff43b81e48fe0c8a76be22c256fc0c2f3c12a96bee50bde86a2730c67395d' },
				"pending": {
				    "0": {},
				    "1": {}
				},
				"possible": {
				    "0": [
					{
					    "name": "a",
					    "time": -1
					}
				    ],
				    "1": []
				},
				"raw": "",
				"time_last": 561273,
				"time_start": 559995,
				"nonce_last": 1
			    },
			    "type": "session"
			}}
		}

		rpcmethods["getaction"] = {
			'call': self.method_getaction,
			'help': {"args": ["action_hash"],
			"return": {
				'type': 'action',
				'hash': '6d9ff43b81e48fe0c8a76be22c256fc0c2f3c12a96bee50bde86a2730c67395d',
				'session': 'ac35439702f82a17065ef6114dd07d8bccaa6fc3a9a99fed3e20f9cd92259352',
				'action': '!a',
				'value': '42',
				'player': 'mjBY56jFYRWXZEoYi8cztm7z8spjBht9iP',
				'time': 561278,
				'nonce': 1 }}
		}

		rpcmethods["getobject"] = {
			'call': self.method_getobject,
			'help': {"args": ["object_hash"],
			"return": {}}
		}

		rpcmethods["getplayerreputation"] = {
			'call': self.method_getplayerreputation,
			'help': {"args": ["player"],
			"return": {}}
		}

		rpcmethods["info"] = {
			'call': self.method_info,
			'help': {"args": [], "return": {
			    "contracts": 8,
			    "pending": 6,
			    "sessions": 1,
			    "compliance_checks": 1,
			    "time": 561596
			}}
		}

		rpcmethods["validatecontract"] = {
			'call': self.method_validatecontract,
			'help': {"args": ["contract_xml"],
			"return": {"valid": "True if contract_xml is valid"}}
		}

		rpcmethods["dualcontract"] = {
			'call': self.method_dualcontract,
			'help': {"args": ["contract_xml"],
			"return": {"contract": "The dual contract"}}
		}

		rpcmethods["translatecontract"] = {
			'call': self.method_translatecontract,
			'help': {"args": ["contract"],
			"return": {"contract": "Contract in xml format"}}
		}

		rpcmethods["checkcontractscompliance"] = {
			'call': self.method_checkcontractscompliance,
			'help': {"args": ["contract1_xml", "contract2_xml"],
			"return": {"compliant": "True if contracts are compliant"}}
		}


		errors = {
			'CONTRACT_NOT_PRESENT': {'code': -2, 'message': 'Contract not present'},
			'SESSION_NOT_PRESENT': {'code': -3, 'message': 'Session not present'},
			'CONTRACT_ALREADY_FUSED': {'code': -4, 'message': 'Contract already fused'},
			'ACTION_NOT_PRESENT': {'code': -5, 'message': 'Action not present'},
			'CONTRACT_BAD_XML': {'code': -6, 'message': 'Contract bad XML'},
			'INVALID_LIST_TYPE': {'code': -7, 'message': 'Invalid query type'},
			'OBJECT_NOT_PRESENT': {'code': -8, 'message': 'Object not present'},
			'CONTRACTS_NOT_COMPLIANT': {'code': -9, 'message': 'Contracts not compliant'}
		}

		super (TSTAPI, self).__init__(core, dht, rpcmethods, errors)

		#self.method_tell ('<contract><intaction id="test" /></contract>', 'mn1FwcHcUDodajXGUFRdzx23BpGU7GJ7DV', 100)
		#self.method_accept ('8a4ae92bb250caa3abc8ef347a37f61f1edc290333fb58af816235f9a920c406', 'moRyzcLkAzN3kqwmFwMV2E5RLuK4SFCHyg')


	# Return compliant list of a contract
	def method_compliantwithcontract (self, contracthash):
		r = { 'contracts': self.vm.getCompliantWithContract (contracthash) }
		return r

	def method_broadcast_custom (self, thex, temp_id):
		r = self.api.method_broadcast (thex, temp_id)
		if r['txid'] != None:
			self.vm.postBroadcastOfContract (temp_id, r['txid'])
		return r

	# Message-creation operations
	def method_tell (self, contract, player, expire):
		message = TSTMessage.tell (contract, player, int (expire))
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)

		self.vm.preBroadcastOfContract (tempid)
		r = { 'outscript': outscript, 'datahash': datahash, 'tempid': tempid, 'fee': Protocol.estimateFee (self.vm.getChainCode (), int (expire) * len (contract)) }
		return r

	def method_do (self, session, action, value, nonce, player):
		message = TSTMessage.do (session, action, value, nonce, player)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		return { 'outscript': outscript, 'datahash': datahash, 'tempid': tempid, 'fee': Protocol.estimateFee (self.vm.getChainCode (), int (100) * len (action))  }


	def method_fuse (self, contractp, contractq, player):
		cp = self.vm.getContract (contractp)['contract']
		cq = self.vm.getContract (contractq)['contract']

		try:
			if not Tibet.checkContractsCompliance (cp, cq):
				return self.createErrorResponse ('CONTRACTS_NOT_COMPLIANT')
		except Tibet.BadXMLException:
			return self.createErrorResponse ('CONTRACT_BAD_XML')

		message = TSTMessage.fuse (contractp, contractq, player)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		return { 'outscript': outscript, 'datahash': datahash, 'tempid': tempid, 'fee': Protocol.estimateFee (self.vm.getChainCode (), int (100) * len (player))  }


	def method_accept (self, contractq, player):
		cq = self.vm.getContract (contractq)['contract']
		cp = Tibet.dualContract (cq)

		try:
			if not Tibet.checkContractsCompliance (cp, cq):
				return self.createErrorResponse ('CONTRACTS_NOT_COMPLIANT')
		except Tibet.BadXMLException:
			return self.createErrorResponse ('CONTRACT_BAD_XML')

		message = TSTMessage.accept (contractq, player)
		[datahash, outscript, tempid] = message.toOutputScript (self.dht)
		return { 'outscript': outscript, 'datahash': datahash, 'tempid': tempid, 'fee': Protocol.estimateFee (self.vm.getChainCode (), int (100) * len (player))  }



	# Static operations
	def method_validatecontract (self, c):
		try:
			return {"valid": Tibet.validateContract (c)}
		except Tibet.BadXMLException:
			return self.createErrorResponse ('CONTRACT_BAD_XML')

	def method_translatecontract (self, c):
		return {"contract": Tibet.translateContract (c)}


	def method_dualcontract (self, c):
		try:
			return {"contract": Tibet.dualContract (c)}
		except Tibet.BadXMLException:
			return self.createErrorResponse ('CONTRACT_BAD_XML')


	# Compliance
	def method_checkcontractscompliance (self, c1, c2):
		try:
			return {"compliant": Tibet.checkContractsCompliance (c1, c2)}
		except Tibet.BadXMLException:
			return self.createErrorResponse ('CONTRACT_BAD_XML')




	# State query operations
	def method_listcontracts (self, type):
		clist = self.vm.listContracts (type)
		if clist == None:
			return self.createErrorResponse ('INVALID_LIST_TYPE')
		else:
			return clist

	def method_listsessions (self, type):
		slist = self.vm.listSessions (type)
		if slist == None:
			return self.createErrorResponse ('INVALID_LIST_TYPE')
		else:
			return slist

	def method_getcontract (self, contracthash):
		c = self.vm.getContract (contracthash)
		if c == None:
			return self.createErrorResponse ('CONTRACT_NOT_PRESENT')
		else:
			return c



	def method_getplayerreputation (self, player):
		c = self.vm.getPlayerReputation (player)
		return {'reputation': c}


	def method_getobject (self, objecthash):
		s = self.vm.inspectObjectType (objecthash)

		if s == None:
			return self.createErrorResponse ('OBJECT_NOT_PRESENT')
		else:
			if s == 'session':
				return self.method_getsession (objecthash)
			elif s == 'contract':
				return self.method_getcontract (objecthash)
			elif s == 'action':
				return self.method_getaction (objecthash)
			else:
				return self.createErrorResponse ('OBJECT_NOT_PRESENT')


	def method_getsession (self, sessionhash):
		s = self.vm.getSession (sessionhash)
		if s == None:
			return self.createErrorResponse ('SESSION_NOT_PRESENT')
		else:
			ss = copy.deepcopy (s)
			ss['state']['raw'] = ''
			return ss

	def method_getaction (self, actionhash):
		a = self.vm.getAction (actionhash)
		if a == None:
			return self.createErrorResponse ('ACTION_NOT_PRESENT')
		else:
			return a


	# Return tstvm informations
	def method_info (self):
		return (self.vm.getChainState ())
