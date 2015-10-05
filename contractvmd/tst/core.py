# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, dapp
from ..proto import Protocol
from .sessioninstance import SessionInstance
from .tibet import Tibet


logger = logging.getLogger(config.APP_NAME)


# Virtual Machine for contract/session handling
class TSTCore (dapp.Core):
	def __init__ (self, chain, database):
		super (TSTCore, self).__init__ (chain, database)

		self.database.init ('Contracts', [])
		self.database.init ('ContractsPending', [])
		self.database.init ('ContractsExpired', [])
		self.database.init ('ContractsFused', [])
		self.database.init ('ContractsEnded', [])

		self.database.init ('ContractsBroadcasted', {})
		self.database.init ('ContractsPreBroadcast', [])

		self.database.init ('Sessions', [])
		self.database.init ('SessionsRunning', [])
		self.database.init ('SessionsEnded', [])

		self.database.init ('Actions', [])

		self.database.init ('ComplianceChecks', 0)


	# Called during a tell pre broadcast
	def preBroadcastOfContract (self, tempid):
		if not str(tempid) in self.database.get ('ContractsPreBroadcast'):
			self.database.listappend ('ContractsPreBroadcast', str (tempid))

		#print (self.database.get ('ContractsPreBroadcast'))


	# Called during a tell post broadcast
	def postBroadcastOfContract (self, tempid, contracthash):
		if str (tempid) in self.database.get ('ContractsPreBroadcast'):
			self.database.listremove ('ContractsPreBroadcast', str (tempid))
		if not str (contracthash) in self.database.get ('ContractsPreBroadcast'):
			self.database.listappend ('ContractsPreBroadcast', str (contracthash))
		#print (self.database.get ('ContractsBroadcasted'))

	# Return contracts compliant with given contract
	def getCompliantWithContract (self, contracthash):
		if contracthash in self.database.get ('ContractsBroadcasted'):
			clist = self.database.get ('ContractsBroadcasted')
			return clist[contracthash]
		else:
			return []


	def checkContractsCompliance (self, contractphash, contractqhash):
		contractp = self.database.get (contractphash)
		contractq = self.database.get (contractqhash)

		# Check contracts compliance
		self.database.intinc ('ComplianceChecks')
		if not Tibet.checkContractsCompliance (contractp['contract'], contractq['contract']):
			return False
		else:
			return True

	def listContracts (self, type):
		if type == 'all':
			return self.database.get ('Contracts')
		elif type == 'pending':
			return self.database.get ('ContractsPending')
		elif type == 'expired':
			return self.database.get ('ContractsExpired')
		elif type == 'fused':
			return self.database.get ('ContractsFused')
		elif type == 'ended':
			return self.database.get ('ContractsEnded')
		else:
			return self.database.get ('Contracts')

	def listSessions (self, type):
		if type == 'all':
			return self.database.get ('Sessions')
		elif type == 'running':
			return self.database.get ('SessionsRunning')
		elif type == 'ended':
			return self.database.get ('SessionsEnded')
		else:
			return self.database.get ('Sessions')

	def getPlayerReputation (self, player):
		c = self.database.get (player)

		if c != None:
			return c['reputation']
		else:
			return 0.0

	def getContract (self, contracthash):
		c = self.database.get (contracthash)
		#print (c, contracthash)

		if c != None and c['type'] == 'contract':
			if c['state'] == 'pending' and c['expiry'] + c['time'] < self.getTime ():
				c = self.markContractAsExpired (c)

			return c
		else:
			return None

	def getSession (self, sessionhash):
		s = self.database.get (sessionhash)
		if s != None and s['type'] == 'session':
			# The time pass, recompute the session-state
			#print (int (self.getTime ()), int (s['state']['time_last']))
			#not s['state']['end'] and
			if (int (self.getTime ()) > int (s['state']['time_last'])):
				sob = SessionInstance (s).update (self.getTime ())
				self.database.set (sessionhash, sob)
				self.updateSessionObjects (sob)
				return sob
			else:
				return s
		else:
			return None

	def getAction (self, actionhash):
		a = self.database.get (actionhash)

		if a != None and a['type'] == 'action':
			return a
		else:
			return None


	def inspectObjectType (self, objecthash):
		a = self.database.get (objecthash)

		if a != None and ('type' in a):
			return a['type']
		else:
			return None


	def getChainState (self):
		return {'contracts': len (self.listContracts('all')), 'contracts_pending': len (self.listContracts('pending')),
			'contracts_fused': len (self.listContracts('fused')), 'contracts_expired': len (self.listContracts('expired')),
			'contracts_ended': len (self.listContracts('ended')),
			'sessions': len (self.listSessions('all')), 'sessions_running': len (self.listSessions('running')),
			'sessions_ended': len (self.listSessions('ended')), 'time': self.getTime (),
			'compliance_checks': int (self.database.get('ComplianceChecks'))}


	## VM functions
	def tell (self, contracthash, contract, player, expiry, time):
		if self.database.exists (contracthash):
			logger.error ('Contract %s already exists', contracthash)
			return None

		# Validate contract
		if not Tibet.validateContract (contract):
			logger.error ('Invalid contract %s', contracthash)

		ob = { 'type': 'contract', 'state': 'pending', 'hash': contracthash, 'contract': contract, 'session': None,
			'player': player, 'expiry': expiry, 'time': time }
		self.database.set (contracthash, ob)
		self.database.listappend ('ContractsPending', contracthash)
		self.database.listappend ('Contracts', contracthash)

		# Update player
		if not self.database.exists (player):
			self.database.set (player, {'reputation': 0.0})


		# Update broadcast list
		if contracthash in self.database.get ('ContractsPreBroadcast'):
			self.database.listremove ('ContractsPreBroadcast', contracthash)

			clist = self.database.get ('ContractsBroadcasted')
			clist[contracthash] = []
			self.database.set ('ContractsBroadcasted', clist)

		# Update compliant list
		cblist = self.database.get ('ContractsBroadcasted')
		# Altrimenti controllo la compliant di questo contratto con i contratti pendenti
		if not contracthash in cblist:
			for othercontracthash in cblist:
				if self.checkContractsCompliance (contracthash, othercontracthash):
					cblist[othercontracthash].append (contracthash)
					self.database.set ('ContractsBroadcasted', cblist)
					logger.info ('Found compliant %s <=> %s',othercontracthash, contracthash)
		# Se il contratto e' stato broadcastato da questo nodo, controllo la compliant con i pendenti
		else:
			for othercontracthash in self.database.get ('ContractsPending'):
				if self.checkContractsCompliance (contracthash, othercontracthash):
					cblist[contracthash].append (othercontracthash)
					self.database.set ('ContractsBroadcasted', cblist)
					logger.info ('Found compliant %s <=> %s',othercontracthash, contracthash)


	def accept (self, sessionhash, contracthash, player, time):
		if self.database.exists (sessionhash):
			logger.error ('Session %s already exists', sessionhash)
			return None

		if not self.database.exists (contracthash):
			logger.error ('Contract %s doesn\'t exists', contracthash)
			return None

		if not contracthash in self.database.get ('ContractsPending'):
			logger.error ('Contract %s already fused', contracthash)
			return None


		contract = self.database.get (contracthash)

		if contract['expiry'] + contract['time'] < time:
			fr = self.getTime () - (contract['expiry'] + contract['time'])
			logger.error ('Contract %s expired from %d time units', contracthash, fr)
			self.markContractAsExpired (contract)
			return False


		# Make the dual contract
		try:
			contract_dual = Tibet.dualContract (contract['contract'])
		except Tibet.TibetBadXMLException:
			logger.error ('Failed to create dual contract of %s', contract['contract'])
			return False


		# Fuse the session
		sob = {'type': 'session', 'hash': sessionhash,
			'players': {contract['player']: '0', player: '1'},
			'contracts': {contract['player']: contracthash, player: sessionhash}, 'state': {}}

		# Update the session state
		si = SessionInstance (sob)
		si.fuse (contract['contract'], contract_dual, time)
		sob = si.update (self.getTime ())
		self.updateSessionObjects (sob)

		# Set contract sessionhash
		contract['session'] = sessionhash
		contract['state'] = 'fused'
		self.database.set (contracthash, contract)

		# Update statedb
		self.database.set (sessionhash, sob)
		self.database.listappend ('Sessions', sessionhash)
		self.database.listappend ('SessionsRunning', sessionhash)
		self.database.listremove ('ContractsPending', contracthash)
		self.database.listappend ('ContractsFused', contracthash)



		# Update player
		if not self.database.exists (player):
			self.database.set (player, {'reputation': 0.0})


		if contracthash in self.database.get ('ContractsBroadcasted'):
			slist = self.database.get ('ContractsBroadcasted')
			del slist[contracthash]
			self.database.set ('ContractsBroadcasted', slist)

		return True


	def fuse (self, sessionhash, contractphash, contractqhash, player, time):
		if self.database.exists (sessionhash):
			logger.error ('Session %s already exists', sessionhash)
			return None

		if not self.database.exists (contractphash):
			logger.error ('Contract %s doesn\'t exists', contractphash)
			return None

		if not self.database.exists (contractqhash):
			logger.error ('Contract %s doesn\'t exists', contractphash)
			return None

		if not contractphash in self.database.get ('ContractsPending'):
			logger.error ('Contract %s already fused', contractphash)
			return None

		if not contractqhash in self.database.get ('ContractsPending'):
			logger.error ('Contract %s already fused', contractqhash)
			return None


		contractp = self.database.get (contractphash)
		contractq = self.database.get (contractqhash)

		# Check contracts compliance
		self.database.intinc ('ComplianceChecks')
		if not Tibet.checkContractsCompliance (contractp['contract'], contractq['contract']):
			logger.error ('Contracts [%s, %s] are not compliant', contractphash, contractqhash)
			return False

		# Check if the player is the owner of one of the contracts
		if player != contractp['player'] and player != contractq['player']:
			logger.error ('The player %s is not the owner of one of those contracts [%s, %s]', player, contractphash, contractqhash)
			return False

		# Check contract expiration
		if contractp['expiry'] + contractp['time'] < time:
			fr = self.getTime () - (contractp['expiry'] + contractp['time'])
			logger.error ('Contract %s expired from %d time units', contractphash, fr)
			self.markContractAsExpired (contractp)
			return False

		if contractq['expiry'] + contractq['time'] < time:
			fr = self.getTime () - (contractq['expiry'] + contractq['time'])
			logger.error ('Contract %s expired from %d time units', contractqhash, fr)
			self.markContractAsExpired (contractp)
			return False

		# Create the session object
		sob = {'type': 'session', 'hash': sessionhash,
			'players': {contractp['player']: '0', contractq['player']: '1'},
			'contracts': {contractp['player']: contractphash, contractq['player']: contractqhash}, 'state': {}}

		# Update the session state
		si = SessionInstance (sob)
		si.fuse (contractp['contract'], contractq['contract'], time)
		sob = si.update (self.getTime ())

		self.updateSessionObjects (sob)

		# Set contract sessionhash
		contractp['session'] = sessionhash
		contractq['session'] = sessionhash
		contractp['state'] = 'fused'
		contractq['state'] = 'fused'
		self.database.set (contractphash, contractp)
		self.database.set (contractqhash, contractq)

		# Update statedb
		self.database.set (sessionhash, sob)
		self.database.listappend ('Sessions', sessionhash)
		self.database.listappend ('SessionsRunning', sessionhash)
		self.database.listremove ('ContractsPending', contractphash)
		self.database.listremove ('ContractsPending', contractqhash)
		self.database.listappend ('ContractsFused', contractphash)
		self.database.listappend ('ContractsFused', contractqhash)

		if contractphash in self.database.get ('ContractsBroadcasted'):
			slist = self.database.get ('ContractsBroadcasted')
			del slist[contractphash]
			self.database.set ('ContractsBroadcasted', slist)
		if contractqhash in self.database.get ('ContractsBroadcasted'):
			slist = self.database.get ('ContractsBroadcasted')
			del slist[contractqhash]
			self.database.set ('ContractsBroadcasted', slist)

		return True


	def do (self, sessionhash, actionhash, action, value, nonce, player, time):
		# Get the sessionhash state
		if not self.database.exists (sessionhash):
			logger.error ('Session %s doesn\' exists', sessionhash)
			return False

		if self.database.exists (actionhash):
			logger.error ('Action %s already exists', actionhash)
			return False

		# Validate action (TODO use a regexp)
		if action[0] != '?' and action[0] != '!':
			logger.error ('Invalid action %s', action)
			return False

		session = self.database.get (sessionhash)

		# Check if the player is one of the session player
		if not player in session['players']:
			logger.error ('Cannot perform action %s, %s is not a player of %s', actionhash, player, sessionhash)
			return False

		# Validate nonce
		if int (nonce) <= int (session['state']['nonce_last']):
			logger.error ('Cannot perform action %s, nonce %d <= %d', actionhash, int (nonce), int (session['state']['nonce_last']))
			return False

		# Update the session
		si = SessionInstance (session)
		res = si.do (actionhash, action, value, nonce, player, time)

		if not res:
			logger.error ('Failed to run action %s', action)
		else:
			sob = si.update (self.getTime ())
			self.updateSessionObjects (sob)

			# TODO If there is a pending value and it's a !, the call cannot be performed

			# Add the action, save the state
			aob = { 'type': 'action', 'hash': actionhash, 'session': sessionhash, 'nonce': nonce,
					'action': action, 'value': value, 'player': player, 'time': time }
			self.database.set (actionhash, aob)
			self.database.listappend ('Actions', actionhash)
			self.database.set (sessionhash, sob)

		return res


	def markContractAsExpired (self, c):
		c['state'] = 'expired'
		self.database.listremove ('ContractsPending', c['hash'])
		self.database.listappend ('ContractsExpired', c['hash'])
		self.database.set (c['hash'], c)


	def updatePlayerReputation (self, player, value = None, increment = 0):
		if self.database.exists (player):
			rs = self.database.get (player)
		else:
			rs = {'reputation': 0.0}

		if value == None:
			rs['reputation'] += increment
		else:
			rs['reputation'] = value
		self.database.set (player, rs)


	# Given a session object, update session, contracts and reputation
	def updateSessionObjects (self, sob):
		# If a contract is in an ended session, put it in ended state and list
		# If a session is in an ended session, put it in ended list
		if sob['state']['end'] and not sob['hash'] in self.database.get ('SessionsEnded'):
			self.database.listremove ('SessionsRunning', sob['hash'])
			self.database.listappend ('SessionsEnded', sob['hash'])
			for c in sob['contracts']:
				if sob['contracts'][c] in sob['hash']:
					continue

				self.database.listremove ('ContractsFused', sob['contracts'][c])
				self.database.listappend ('ContractsEnded', sob['contracts'][c])
				d = self.database.get (sob['contracts'][c])
				d['state'] = 'ended'
				self.database.set (sob['contracts'][c], d)

				# Update reputation for players, but we should avoid to increment reputation multiple times
				self.updatePlayerReputation (d['player'], increment = (-1 if sob['state']['culpable'][sob['players'][c]] else 1))
