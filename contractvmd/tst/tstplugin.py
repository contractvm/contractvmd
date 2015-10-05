# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from .. import config, dapp
from . import core, api, proto

logger = logging.getLogger(config.APP_NAME)


class TSTDapp (dapp.Dapp):
	def __init__ (self, chain, db, dht, apimaster):
		self.core = core.TSTCore (chain, db)
		apip = api.TSTAPI (self.core, dht, apimaster)
		super (TSTDapp, self).__init__('TST', proto.TSTProto.DAPP_CODE, proto.TSTProto.METHOD_LIST, chain, db, dht, apip)

	def handleMessage (self, m):
		if m.Method == proto.TSTProto.METHOD_TELL:
			logger.pluginfo ('Found new message %s: tell', m.Hash)

			if not 'contract' in m.Data:
				return False
			else:
				m.Contract = m.Data['contract']

				# Get fee and estimate expiry time
				m.Expire = 100

				# TODO check for expire validity

				return self.core.tell (m.Hash, m.Contract, m.Player, m.Expire, self.core.getTime (m.Block))


		elif m.Method == proto.TSTProto.METHOD_DO:
			logger.pluginfo ('Found new message %s: do', m.Hash)

			if (not ('action' in m.Data) or not ('sessionhash' in m.Data) or not ('nonce' in m.Data) or not ('value' in m.Data)):
				return False
			else:
				m.Action = m.Data['action']
				m.Session = m.Data['sessionhash']
				m.Nonce = int (m.Data['nonce'])
				m.Value = m.Data['value']

				return self.core.do (m.Session, m.Hash, m.Action, m.Value, m.Nonce, m.Player, self.core.getTime (m.Block))


		elif m.Method == proto.TSTProto.METHOD_FUSE:
			logger.pluginfo ('Found new message %s: fuse', m.Hash)

			if (not ('contractphash' in m.Data) or not ('contractqhash' in m.Data)):
				return None
			else:
				m.ContractP = m.Data['contractphash']
				m.ContractQ = m.Data['contractqhash']

				return self.core.fuse (m.Hash, m.ContractP, m.ContractQ, m.Player, self.core.getTime (m.Block))


		elif m.Method == proto.TSTProto.METHOD_ACCEPT:
			logger.pluginfo ('Found new message %s: accept', m.Hash)

			if (not ('contracthash' in m.Data)):
				return False
			else:
				m.Contract = m.Data['contracthash']

				return self.core.accept (m.Hash, m.Contract, m.Player, self.core.getTime (m.Block))
		else:
			return False
