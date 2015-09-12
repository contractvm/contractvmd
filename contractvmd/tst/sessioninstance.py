# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from .tibet import Tibet
from .. import config

import logging


logger = logging.getLogger(config.APP_NAME)


# Session instance class
# Load the instance from db, apply a transformation function, then save the state back in the db
# Only here we can use tibet session related calls (startSession, sessionDoAction, sessionEndState, ...)
class SessionInstance:
	def __init__ (self, session):
		self.session = session

	def fuse (self, contractp, contractq, time):
		sdata = Tibet.startSession (contractp, contractq)

		self.session['state'] = { 'raw': sdata, 'time_start': time, 'time_last': time, 'nonce_last': 0,
			'culpable': {'0': False, '1': False}, 'duty': {'0': False, '1': False}, 'end': False, 'history': {},
			'pending': {'0': {}, '1': {}}, 'possible': {'0': [], '1': []} }


	def do (self, actionhash, action, value, nonce, player, time):
		if self.session['state']['end']:
			logger.error ('The session is in end-state')
			return False

		pid = self.session['players'][player]
		delay_last = int (time) - int (self.session['state']['time_last'])

		# !action
		if action[0] == '!':
			fact = action[1:]

			# THis could be a problem
			#if len (self.session['state']['pending'][pid]) != 0:
			#	logger.error ('Player %s is trying to fire %s but pending is not empty %s', player, action, str (self.session['state']['pending'][pid]))
			#	return False

			# Call the step function
			self.session['state']['raw'] = Tibet.sessionDo (self.session['state']['raw'], fact, pid, delay_last)
			self.session['state']['time_last'] = time
			self.session['state']['pending']['0' if pid == '1' else '1'][fact] = {'action': actionhash, 'value': value}
			self.session['state']['history'][nonce] = actionhash
			self.session['state']['nonce_last'] = nonce

			return True

		# ?action
		elif action[0] == '?':
			qact = action[1:]

			if qact in self.session['state']['pending'][pid]:
				del self.session['state']['pending'][pid][qact]
				self.session['state']['history'][nonce] = actionhash
				self.session['state']['nonce_last'] = nonce
				return True
			else:
				logger.error ('Player %s is trying to fire %s but is not in pending', player, action)
				return False
		return False

	# Return the session object with updated state
	def update (self, time):
		if self.session['state']['end']:
			return self.session

		# Evalute time delays
		delay_last = int (time) - int (self.session['state']['time_last'])
		self.session['state']['time_last'] = time

		# Apply the delay from last update
		self.session['state']['raw'] = Tibet.sessionDelay (self.session['state']['raw'], delay_last)

		# Update readable status


		self.session['state']['duty'] = Tibet.sessionDutyState (self.session['state']['raw'])
		if len (self.session['state']['pending']['0']) > 0:
			self.session['state']['duty']['0'] = True
			self.session['state']['duty']['1'] = False
		if len (self.session['state']['pending']['1']) > 0:
			self.session['state']['duty']['1'] = True
			self.session['state']['duty']['0'] = False

		self.session['state']['culpable'] = Tibet.sessionCulpableState (self.session['state']['raw'])

		# Update possible actions for players
		self.session['state']['possible'] = Tibet.sessionPossibleActions (self.session['state']['raw'])


		# TODO check this end condition
		self.session['state']['end'] = ( Tibet.sessionEndState (self.session['state']['raw'])
			and len (self.session['state']['pending']['0']) == 0 and len (self.session['state']['pending']['1']) == 0 ) or self.session['state']['culpable']['0'] or self.session['state']['culpable']['1']

		if not self.session['state']['end']:
			self.session['state']['end'] = self.session['state']['culpable']['0'] or self.session['state']['culpable']['1']

		logger.pluginfo ('Update session %s', self.session['hash']) #, str(self.session))

		return self.session
